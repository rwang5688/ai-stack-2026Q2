#!/usr/bin/env python3
"""
CloudFormation Template Validation Tests
Feature: code-server-deployment

Tests the CloudFormation template for syntax, security, and compliance.
"""

import json
import yaml
import boto3
from pathlib import Path
import pytest

class TestCloudFormationTemplate:
    """Unit tests for CloudFormation template validation"""
    
    @classmethod
    def setup_class(cls):
        """Load the CloudFormation template"""
        template_path = Path(__file__).parent.parent / "code-server-improved.yaml"
        with open(template_path, 'r') as f:
            cls.template = yaml.safe_load(f)
    
    def test_template_structure(self):
        """Test basic template structure and required sections"""
        assert 'AWSTemplateFormatVersion' in self.template
        assert 'Description' in self.template
        assert 'Parameters' in self.template
        assert 'Resources' in self.template
        assert 'Outputs' in self.template
    
    def test_security_group_configuration(self):
        """
        **Feature: code-server-deployment, Property 3: Security Group Isolation**
        Test that security group only allows CloudFront access
        """
        sg = self.template['Resources']['SecurityGroup']
        ingress_rules = sg['Properties']['SecurityGroupIngress']
        
        # Find HTTP rule
        http_rule = None
        for rule in ingress_rules:
            if rule.get('FromPort') == 80:
                http_rule = rule
                break
        
        assert http_rule is not None, "HTTP rule not found"
        assert 'SourcePrefixListId' in http_rule, "Should use CloudFront prefix list"
        assert 'CidrIp' not in http_rule, "Should not allow open CIDR access"
    
    def test_iam_permissions(self):
        """Test IAM role has required permissions"""
        role = self.template['Resources']['VSCodeInstanceRole']
        managed_policies = role['Properties']['ManagedPolicyArns']
        
        # Check for required policies
        admin_policy = any('AdministratorAccess' in str(policy) for policy in managed_policies)
        ssm_policy = any('AmazonSSMManagedInstanceCore' in str(policy) for policy in managed_policies)
        
        assert admin_policy, "AdministratorAccess policy required"
        assert ssm_policy, "SSM managed instance policy required"
    
    def test_ssm_document_structure(self):
        """
        **Feature: code-server-deployment, Property 1: Bootstrap Completion Verification**
        Test SSM document has all required installation steps
        """
        ssm_doc = self.template['Resources']['VSCodeInstanceSSMDoc']
        main_steps = ssm_doc['Properties']['Content']['mainSteps']
        
        required_steps = [
            'UpdateSystem',
            'InstallNodeJS', 
            'InstallAWSCLI',
            'InstallCDK',
            'InstallCodeServer',
            'ConfigureNginx'
        ]
        
        step_names = [step['name'] for step in main_steps]
        for required_step in required_steps:
            assert required_step in step_names, f"Missing required step: {required_step}"
    
    def test_nodejs_installation_resilience(self):
        """
        **Feature: code-server-deployment, Property 7: Node.js Installation Resilience**
        Test Node.js installation uses reliable method
        """
        ssm_doc = self.template['Resources']['VSCodeInstanceSSMDoc']
        main_steps = ssm_doc['Properties']['Content']['mainSteps']
        
        # Find Node.js installation step
        nodejs_step = None
        for step in main_steps:
            if step['name'] == 'InstallNodeJS':
                nodejs_step = step
                break
        
        assert nodejs_step is not None, "Node.js installation step not found"
        
        commands = nodejs_step['inputs']['runCommand']
        command_text = ' '.join(commands)
        
        # Should use official binary, not NodeSource
        assert 'nodejs.org/dist' in command_text, "Should use official Node.js binary"
        assert 'nodesource.list' in command_text, "Should clean up NodeSource repos"
    
    def test_association_targeting(self):
        """Test SSM association uses reliable instance targeting"""
        association = self.template['Resources']['VSCodeInstanceSSMAssociation']
        targets = association['Properties']['Targets']
        
        # Should use InstanceIds, not tags
        assert len(targets) == 1, "Should have exactly one target"
        assert targets[0]['Key'] == 'InstanceIds', "Should target by InstanceIds"
    
    def test_nginx_configuration(self):
        """
        **Feature: code-server-deployment, Property 5: Configuration Validation**
        Test nginx configuration avoids circular dependencies
        """
        ssm_doc = self.template['Resources']['VSCodeInstanceSSMDoc']
        main_steps = ssm_doc['Properties']['Content']['mainSteps']
        
        # Find nginx configuration step
        nginx_step = None
        for step in main_steps:
            if step['name'] == 'ConfigureNginx':
                nginx_step = step
                break
        
        assert nginx_step is not None, "Nginx configuration step not found"
        
        commands = nginx_step['inputs']['runCommand']
        command_text = ' '.join(commands)
        
        # Should use generic server_name
        assert 'server_name _;' in command_text, "Should use generic server_name"
        assert 'nginx -t' in command_text, "Should validate nginx config"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])