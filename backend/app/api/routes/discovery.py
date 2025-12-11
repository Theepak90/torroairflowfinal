from flask import Blueprint, request, jsonify
from app.services.discovery_service import DiscoveryService
import logging

logger = logging.getLogger(__name__)

discovery_bp = Blueprint('discovery', __name__, url_prefix='/api/discovery')


@discovery_bp.route('', methods=['GET'])
def get_discoveries():
    try:
        # Validate and parse page parameter
        try:
            page = int(request.args.get('page', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid page parameter. Must be a non-negative integer.'}), 400
        
        # Validate page is non-negative
        if page < 0:
            return jsonify({'error': 'Page parameter must be a non-negative integer.'}), 400
        
        # Validate and parse size parameter
        try:
            size = int(request.args.get('size', 50))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid size parameter. Must be a positive integer.'}), 400
        
        # Enforce strict size limits
        if size > 100:
            size = 100
        if size < 1:
            size = 50
        
        status = request.args.get('status')
        environment = request.args.get('environment')
        data_source_type = request.args.get('data_source_type')
        search = request.args.get('search')
        
        discoveries, pagination = DiscoveryService.get_discoveries(
            page=page,
            size=size,
            status=status,
            environment=environment,
            data_source_type=data_source_type,
            search=search
        )
        
        return jsonify({
            'discoveries': discoveries,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting discoveries: {str(e)}")
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>', methods=['GET'])
def get_discovery(discovery_id):
    try:
        discovery = DiscoveryService.get_discovery_by_id(discovery_id)
        
        if not discovery:
            return jsonify({'error': 'Discovery not found'}), 404
        
        return jsonify(discovery), 200
        
    except Exception as e:
        logger.error(f"Error getting discovery {discovery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>/approve', methods=['PUT'])
def approve_discovery(discovery_id):
    try:
        # Validate JSON payload exists
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        approved_by = data.get('approved_by')
        role = data.get('role')
        comments = data.get('comments')
        
        # Validate required field
        if not approved_by or not isinstance(approved_by, str) or not approved_by.strip():
            return jsonify({'error': 'approved_by is required and must be a non-empty string'}), 400
        
        discovery = DiscoveryService.approve_discovery(discovery_id, approved_by, role, comments)
        
        return jsonify({
            'message': 'Discovery approved successfully',
            'discovery': discovery
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error approving discovery {discovery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>/reject', methods=['PUT'])
def reject_discovery(discovery_id):
    try:
        # Validate JSON payload exists
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        rejected_by = data.get('rejected_by')
        rejection_reason = data.get('rejection_reason')
        role = data.get('role')
        comments = data.get('comments')
        
        # Validate required field
        if not rejected_by or not isinstance(rejected_by, str) or not rejected_by.strip():
            return jsonify({'error': 'rejected_by is required and must be a non-empty string'}), 400
        
        discovery = DiscoveryService.reject_discovery(discovery_id, rejected_by, rejection_reason, role, comments)
        
        return jsonify({
            'message': 'Discovery rejected successfully',
            'discovery': discovery
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error rejecting discovery {discovery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = DiscoveryService.get_summary_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
