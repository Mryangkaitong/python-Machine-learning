#!/usr/bin/env bash

# AZURE SETTINGS

# your azure subscription ID (look it up under 'Settings' in the management portal)
# It has the following form '00000000-0000-0000-0000-000000000000'
export AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID:-}

# name for service (must be unique among all azure users), eg. 'ddbazaa'
export AZURE_SERVICE_NAME=${AZURE_SERVICE_NAME:-ddbazaa}

# name for storage account (must be unique among all azure users)
export AZURE_STORAGE_ACCOUNT=${AZURE_STORAGE_ACCOUNT:-ddbazaastore}

# eg. 'Standard_D2', or 'Standard_D14'
export AZURE_ROLE_SIZE=${AZURE_ROLE_SIZE:-Standard_D2}

# EC2 SETTINGS

# For ec-2, we recommend that you keep your AWS_ACCESS_KEY_ID and your
# AWS_SECRET_ACCESS_KEY in ~/.aws/credentials.

# eg. 'm3.large'
#export EC2_INSTANCE_TYPE=${EC2_INSTANCE_TYPE:-r3.4xlarge}
export EC2_INSTANCE_TYPE=m3.2xlarge
