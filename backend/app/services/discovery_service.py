import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.database import get_db_connection
from app.models.discovery import DataDiscovery

logger = logging.getLogger(__name__)


class DiscoveryService:
    @staticmethod
    def get_discoveries(
        page: int = 0,
        size: int = 50,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        data_source_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict], Dict]:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                where_conditions = [
                    "is_visible = TRUE",
                    "is_active = TRUE"
                ]
                params = []
                
                # Validate and sanitize filter parameters
                if status:
                    status = status.strip()[:50]  # Limit length
                    if status:
                        where_conditions.append("status = %s")
                        params.append(status)
                
                if environment:
                    environment = environment.strip()[:50]  # Limit length
                    if environment:
                        where_conditions.append("environment = %s")
                        params.append(environment)
                
                if data_source_type:
                    data_source_type = data_source_type.strip()[:100]  # Limit length
                    if data_source_type:
                        where_conditions.append("data_source_type = %s")
                        params.append(data_source_type)
                
                if search:
                    # Sanitize search input - limit length to prevent DoS
                    search = search.strip()[:500]  # Max 500 characters
                    if search:  # Only add if not empty after strip
                        where_conditions.append("(JSON_EXTRACT(file_metadata, '$.basic.name') LIKE %s OR storage_path LIKE %s)")
                        search_param = f"%{search}%"
                        params.extend([search_param, search_param])
                
                where_clause = " AND ".join(where_conditions)
                
                # Validate offset to prevent negative values
                offset = page * size
                if offset < 0:
                    offset = 0
                
                count_sql = f"SELECT COUNT(*) as total FROM data_discovery WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']
                sql = f"""
                    SELECT * FROM data_discovery
                    WHERE {where_clause}
                    ORDER BY discovered_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, params + [size, offset])
                rows = cursor.fetchall()
                
                discoveries = [DataDiscovery.from_db_row(row) for row in rows]
                
                pagination = {
                    "page": page,
                    "size": size,
                    "total": total,
                    "total_pages": (total + size - 1) // size,
                    "has_next": (page + 1) * size < total,
                    "has_prev": page > 0
                }
                
                return discoveries, pagination
    
    @staticmethod
    def get_discovery_by_id(discovery_id: int) -> Optional[Dict]:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM data_discovery
                    WHERE id = %s
                """
                cursor.execute(sql, (discovery_id,))
                row = cursor.fetchone()
                return DataDiscovery.from_db_row(row)
    
    @staticmethod
    def approve_discovery(discovery_id: int, approved_by: str, role: Optional[str] = None, comments: Optional[str] = None) -> Dict:
        with get_db_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT * FROM data_discovery
                        WHERE id = %s
                    """
                    cursor.execute(sql, (discovery_id,))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        raise ValueError(f"Discovery {discovery_id} not found")
                    
                    existing_approval_workflow = existing.get('approval_workflow') or {}
                    if isinstance(existing_approval_workflow, str):
                        existing_approval_workflow = json.loads(existing_approval_workflow)
                    if not isinstance(existing_approval_workflow, dict):
                        existing_approval_workflow = {}
                    
                    approval_obj = {
                        "by": approved_by,
                        "at": datetime.utcnow().isoformat() + "Z",
                        "role": role or "data_governor",
                        "comments": comments
                    }
                    
                    history = existing_approval_workflow.get('history', []) if isinstance(existing_approval_workflow, dict) else []
                    history.append({
                        "action": "approved",
                        **approval_obj
                    })
                    
                    new_approval_workflow = {
                        "approval": approval_obj,
                        "rejection": None,
                        "history": history
                    }
                    
                    update_sql = """
                        UPDATE data_discovery
                        SET status = 'approved',
                            approval_status = 'approved',
                            approval_workflow = %s,
                            updated_at = NOW()
                        WHERE id = %s
                    """
                    
                    cursor.execute(update_sql, (
                        json.dumps(new_approval_workflow),
                        discovery_id
                    ))
                    
                    conn.commit()
                    
                    return DiscoveryService.get_discovery_by_id(discovery_id)
                    
            except Exception as e:
                conn.rollback()
                logger.error('FN:approve_discovery discovery_id:{} approved_by:{} error:{}'.format(discovery_id, approved_by, str(e)))
                raise
    
    @staticmethod
    def reject_discovery(discovery_id: int, rejected_by: str, rejection_reason: Optional[str] = None, role: Optional[str] = None, comments: Optional[str] = None) -> Dict:
        with get_db_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT * FROM data_discovery
                        WHERE id = %s
                    """
                    cursor.execute(sql, (discovery_id,))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        raise ValueError(f"Discovery {discovery_id} not found")
                    
                    existing_approval_workflow = existing.get('approval_workflow') or {}
                    if isinstance(existing_approval_workflow, str):
                        existing_approval_workflow = json.loads(existing_approval_workflow)
                    if not isinstance(existing_approval_workflow, dict):
                        existing_approval_workflow = {}
                    
                    rejection_obj = {
                        "by": rejected_by,
                        "at": datetime.utcnow().isoformat() + "Z",
                        "role": role or "data_governor",
                        "reason": rejection_reason,
                        "comments": comments
                    }
                    
                    history = existing_approval_workflow.get('history', []) if isinstance(existing_approval_workflow, dict) else []
                    history.append({
                        "action": "rejected",
                        **rejection_obj
                    })
                    
                    new_approval_workflow = {
                        "approval": None,
                        "rejection": rejection_obj,
                        "history": history
                    }
                    
                    update_sql = """
                        UPDATE data_discovery
                        SET status = 'rejected',
                            approval_status = 'rejected',
                            is_visible = FALSE,
                            approval_workflow = %s,
                            updated_at = NOW()
                        WHERE id = %s
                    """
                    
                    cursor.execute(update_sql, (
                        json.dumps(new_approval_workflow),
                        discovery_id
                    ))
                    
                    conn.commit()
                    
                    return DiscoveryService.get_discovery_by_id(discovery_id)
                    
            except Exception as e:
                conn.rollback()
                logger.error('FN:reject_discovery discovery_id:{} rejected_by:{} error:{}'.format(discovery_id, rejected_by, str(e)))
                raise
    
    @staticmethod
    def get_summary_stats() -> Dict:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        COUNT(*) as total_discoveries,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                        SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count
                    FROM data_discovery
                    WHERE is_visible = TRUE
                      AND is_active = TRUE
                """
                cursor.execute(sql)
                return cursor.fetchone()
