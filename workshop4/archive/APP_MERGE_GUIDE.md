# Application Merge Guide: Adding Authentication to Your Streamlit App

## Overview

This guide explains how to merge your local Streamlit application with authentication for deployment. The deployed version requires Cognito authentication, while your local version focuses on application functionality.

## File Structure

```
workshop4/
├── multi_agent_bedrock/app.py          # Local version (no auth)
└── deploy_multi_agent_bedrock/
    └── docker_app/
        ├── app.py                      # Deployed version (with auth template)
        └── default_app.py              # Original auth example
```

## The Merge Process

### Step 1: Understand the Template Structure

The deployed `app.py` is structured in clear sections:

```python
# =============================================================================
# AUTHENTICATION SECTION - Required for Deployed Applications
# =============================================================================
# Authentication setup and enforcement

# =============================================================================
# APPLICATION LOGIC SECTION - Your Custom Application Code Goes Here
# =============================================================================
# Your main application code
```

### Step 2: Copy Your Application Logic

1. **Open both files**: 
   - Source: `workshop4/multi_agent_bedrock/app.py` (your local app)
   - Target: `workshop4/deploy_multi_agent_bedrock/docker_app/app.py` (deployment template)

2. **Identify what to copy**: Copy everything EXCEPT:
   - `import streamlit as st` (already in authentication section)
   - Basic imports that are already present
   - Page configuration (if it conflicts with auth setup)

3. **Copy your application logic**: 
   - System prompts and constants
   - Function definitions
   - Main application flow
   - UI components (but preserve authentication sidebar)

### Step 3: Merge Sidebar Components

The authentication template includes a sidebar with:
- User welcome message
- Logout button
- Divider

**Add your sidebar content AFTER the divider**:

```python
with st.sidebar:
    # Authentication UI (keep this)
    st.header("👤 User Authentication")
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("🚪 Logout", "logout_btn", on_click=logout)
    st.divider()
    
    # Your application UI (add your content here)
    st.header("🤖 AI Service Details")
    # ... rest of your sidebar content
```

### Step 4: Test the Integration

1. **Local Testing**: 
   - Comment out the authentication section for local testing
   - Verify your application logic works

2. **Deployment Testing**:
   - Uncomment authentication section
   - Test that authentication works
   - Verify your application features work after login

## Common Merge Patterns

### Pattern 1: Simple Application

For simple applications, copy everything after the imports:

```python
# AUTHENTICATION SECTION (keep as-is)
# ... authentication code ...

# APPLICATION LOGIC SECTION (replace with your code)
# Copy your constants, functions, and main logic here
```

### Pattern 2: Complex Multi-Agent Application

For complex applications like the multi-agent system:

1. Copy all system prompts and constants
2. Copy all function definitions
3. Copy the main application flow
4. Merge sidebar components carefully

### Pattern 3: Custom Configuration

If your app has custom configuration:

1. Keep authentication configuration at the top
2. Add your configuration after authentication
3. Ensure no conflicts between auth and app config

## Environment Variables

The template includes environment variable setup for:
- `STRANDS_KNOWLEDGE_BASE_ID`: Set in Dockerfile
- `BYPASS_TOOL_CONSENT`: Set in application
- Authentication variables: Managed by CDK/Secrets Manager

## Troubleshooting

### Authentication Issues
- Verify Cognito resources are deployed
- Check Secrets Manager configuration
- Ensure authentication imports are correct

### Application Issues
- Test application logic separately from authentication
- Verify all imports are available in the container
- Check environment variables are set correctly

### Merge Conflicts
- Keep authentication section intact
- Don't duplicate imports
- Preserve authentication UI in sidebar

## Best Practices

1. **Always test locally first** (with auth commented out)
2. **Keep authentication section unchanged**
3. **Add clear comments** for future maintenance
4. **Test both authentication and application features**
5. **Document any custom configuration**

## Example: Multi-Agent System Merge

Here's how the multi-agent system was merged:

```python
# AUTHENTICATION SECTION (unchanged)
# ... authentication setup ...

# APPLICATION LOGIC SECTION (copied from local)
# System prompts
TEACHER_SYSTEM_PROMPT = """..."""
ACTION_DETERMINATION_PROMPT = """..."""
# ... other prompts ...

# Configuration
KB_ID = os.getenv("STRANDS_KNOWLEDGE_BASE_ID", DEFAULT_KB_ID)
# ... other config ...

# Functions
def determine_action(query):
    # ... function logic ...

# Main application
st.title("🎓 TeachAssist - Multi-Agent System")
# ... rest of application ...
```

## Documentation Integration

This merge process should be documented in:
- `MULTI_AGENT_BEDROCK.md` - Deployment section
- `MULTI_AGENT_SAGEMAKER_AI.md` - Similar process for SageMaker

The documentation should include:
1. **Local Development**: How to run without authentication
2. **Deployment Preparation**: How to merge authentication
3. **Testing**: How to verify both auth and functionality work

---

**Remember**: Authentication is required for deployment but optional for local development. The template makes it easy to toggle between both modes.