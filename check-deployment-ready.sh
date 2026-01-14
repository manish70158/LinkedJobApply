#!/bin/bash
# Azure Deployment Checklist Script

echo "========================================="
echo "Azure Deployment Readiness Checklist"
echo "========================================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check and report
check_item() {
    local description=$1
    local command=$2
    
    echo -n "Checking: $description... "
    
    if eval "$command" &> /dev/null; then
        echo "✓ PASS"
        ((CHECKS_PASSED++))
        return 0
    else
        echo "✗ FAIL"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "1. Prerequisites"
echo "----------------"
check_item "Docker installed" "command -v docker"
check_item "Azure CLI installed" "command -v az"
check_item "Git installed" "command -v git"
echo ""

echo "2. Azure Authentication"
echo "----------------------"
check_item "Logged into Azure" "az account show"
if az account show &> /dev/null; then
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo "   Using subscription: $SUBSCRIPTION"
fi
echo ""

echo "3. Required Files"
echo "----------------"
check_item "Dockerfile.azure exists" "test -f Dockerfile.azure"
check_item "azure-deploy.bicep exists" "test -f azure-deploy.bicep"
check_item "azure-deploy.sh exists" "test -f azure-deploy.sh"
check_item "azure-start.sh exists" "test -f azure-start.sh"
check_item "scheduler.py exists" "test -f scheduler.py"
check_item "upload_logs_to_azure.py exists" "test -f upload_logs_to_azure.py"
echo ""

echo "4. Configuration Files"
echo "---------------------"
check_item "config/secrets.py exists" "test -f config/secrets.py"
check_item "config/personals.py exists" "test -f config/personals.py"
check_item "config/search.py exists" "test -f config/search.py"
check_item "requirements.txt exists" "test -f requirements.txt"
echo ""

echo "5. Application Files"
echo "-------------------"
check_item "runAiBot.py exists" "test -f runAiBot.py"
check_item "app.py exists" "test -f app.py"
echo ""

echo "6. Scripts are Executable"
echo "------------------------"
check_item "azure-deploy.sh is executable" "test -x azure-deploy.sh"
check_item "azure-start.sh is executable" "test -x azure-start.sh"
check_item "test-azure-setup.sh is executable" "test -x test-azure-setup.sh"
echo ""

echo "========================================="
echo "Summary"
echo "========================================="
echo "Checks passed: $CHECKS_PASSED"
echo "Checks failed: $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "✓ All checks passed! Ready to deploy to Azure."
    echo ""
    echo "Next steps:"
    echo "1. Review your configuration in config/ directory"
    echo "2. (Optional) Test locally: ./test-local-docker.sh"
    echo "3. Deploy to Azure: ./azure-deploy.sh"
    echo ""
    echo "For detailed instructions, see: AZURE_DEPLOYMENT.md"
else
    echo "✗ Some checks failed. Please fix the issues above before deploying."
    echo ""
    echo "Common fixes:"
    echo "- Install missing tools (Docker, Azure CLI)"
    echo "- Run: az login"
    echo "- Run: chmod +x *.sh"
fi

echo ""
