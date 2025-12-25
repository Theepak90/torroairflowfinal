#!/bin/bash
echo "=========================================="
echo "REMOTE SERVER CHECKLIST"
echo "=========================================="
echo ""

echo "1. Check if backend is running:"
echo "   ps aux | grep -E 'app.main|gunicorn|flask'"
echo ""

echo "2. Test backend directly:"
echo "   curl http://127.0.0.1:5001/api/discovery/stats"
echo ""

echo "3. Check Nginx config:"
echo "   sudo nginx -t"
echo "   cat /etc/nginx/sites-enabled/* | grep -A 10 'location /api'"
echo ""

echo "4. Check if backend port is listening:"
echo "   netstat -an | grep 5001"
echo "   OR"
echo "   lsof -i :5001"
echo ""

echo "5. Check Nginx error logs:"
echo "   sudo tail -f /var/log/nginx/error.log"
echo ""

echo "=========================================="
