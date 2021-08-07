#!/bin/sh -e
set -e


DS_GITHUB_HOSTS_SETTING= && . ./script/domain_lookup.sh && resolve_domain "dsgithub.trendmicro.com" && echo "$HOSTS_SETTING" | tee -a /etc/hosts
ACCESS_DS_TOKEN=$(mgcp-cicd secret get-secret --key access_ds_github_ee_token)

# Get sha of master branch
MASTER_SHA=$(mgcp-cicd git get-branch-sha --repo ${REPO} --github-ee ${GITHUB_EE} --branch master --token ${ACCESS_DS_TOKEN})
echo "Master hash: ${MASTER_SHA}"

# Create PR Branch
timestamp=$(date +%s)
PR_BRANCH=elpis/auto-created-${timestamp}
echo "PR branch: ${PR_BRANCH}"
      
# Get App Version
CONTENT=${DEPLOY_VERSION}
echo "Deploy version: ${CONTENT}"
      
# Create PR Branch
mgcp-cicd git create-branch --repo ${REPO} --github-ee ${GITHUB_EE} --branch ${PR_BRANCH} --base-sha ${MASTER_SHA} --token ${ACCESS_DS_TOKEN}

# Get hash of PR Branch
PR_BRANCH_SHA=$(mgcp-cicd git get-branch-sha --repo ${REPO} --github-ee ${GITHUB_EE} --branch ${PR_BRANCH} --token ${ACCESS_DS_TOKEN})
echo "PR branch hash: ${PR_BRANCH_SHA}"

# Get hash of version.txt
FILE_SHA=$(mgcp-cicd git get-file-sha --repo ${REPO} --github-ee ${GITHUB_EE} --branch-sha ${PR_BRANCH_SHA} --file ${VERSION_FILE} --token ${ACCESS_DS_TOKEN})
echo "File hash: ${FILE_SHA}"

# Update version number in ${VERSION_FILE}
mgcp-cicd git create-file-contents --repo ${REPO} --github-ee ${GITHUB_EE} --branch ${PR_BRANCH} --path ${VERSION_FILE} --file-hash ${FILE_SHA} --content ${DEPLOY_VERSION} --token ${ACCESS_DS_TOKEN}

# Create Pull Request
mgcp-cicd git create-pr --repo ${REPO} --github-ee ${GITHUB_EE} --branch ${PR_BRANCH} --token ${ACCESS_DS_TOKEN}
