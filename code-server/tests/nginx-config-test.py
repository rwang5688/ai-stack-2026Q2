#!/usr/bin/env python3
"""
Test script to validate nginx configuration fixes
"""

def test_nginx_configuration():
    """Test that nginx configuration properly disables default site and validates config"""
    
    with open('code_server/code-server-improved.yaml', 'r') as f:
        content = f.read()
    
    # Test 1: Should remove default nginx site
    assert 'rm -f /etc/nginx/sites-enabled/default' in content, \
        "Should remove default nginx site"
    
    # Test 2: Should validate nginx config before restart
    assert 'nginx -t' in content, \
        "Should validate nginx configuration before restart"
    
    # Test 3: Should use generic server_name
    assert 'server_name _;' in content, \
        "Should use generic server_name"
    
    # Test 4: Should proxy to code-server on port 8080
    assert 'proxy_pass http://localhost:8080/' in content, \
        "Should proxy to code-server on port 8080"
    
    # Test 5: Should enable WebSocket support
    assert 'proxy_set_header Upgrade \\$http_upgrade' in content, \
        "Should enable WebSocket support"
    
    print("✅ All nginx configuration tests passed!")
    return True

if __name__ == "__main__":
    test_nginx_configuration()