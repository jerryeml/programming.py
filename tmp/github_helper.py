
import os
import time
import base64
import logging
import requests
from urllib.parse import urljoin
from typing import List, Optional
from dotenv import load_dotenv


LOG = logging.getLogger(__name__)


class GitHubClient(object):
    def __init__(self, repo: str, token=None, timeout_sec=10):
        self._base_url = f'https://dsgithub.trendmicro.com/api/v3/repos/deep-security/{repo}/'
        self._session = requests.Session()
        self._token = token
        self._timeout_sec = timeout_sec
        self.repo = repo

    def _headers(self) -> dict:
        return {'Authorization': f'token {self.token}'}

    def _tags(self) -> List[dict]:
        """Get tags list
        Response:
        [
          {
            "name": "1.1.188",
            "zipball_url": "https://ds.github.trendmicro.com/api/v3/repos/commercial-mgcp/infra/zipball/1.1.188",
            "tarball_url": "https://ds.github.trendmicro.com/api/v3/repos/commercial-mgcp/infra/tarball/1.1.188",
            "commit": {
              "sha": "6672ae61473c4c16a55654bac827a20bba4b2085",
              "url": "https://ds.github.trendmicro.com/api/v3/repos/commercial-mgcp/infra//commits/6672ae61473c4c16a55654bac827a20bba4b2085"
            },
            "node_id": "MDM6UmVmNjk1OjEuMS4xODg="
          }
        ]
        """
        req_url = urljoin(self._base_url, 'tags')

        LOG.info('Get tags from %s', req_url)

        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)

        response.raise_for_status()

        for tag in response.json():
            tag_data = {'name': tag['name'],
                        'commit_id': tag['commit']['sha']}
            yield tag_data

    @property
    def token(self):
        if self._token is None:
            # get from env var first
            try:
                LOG.info('Get github token from env var')
                self._token = os.environ('github_pat')
                return self._token
            except Exception as ex:
                LOG.info('Cannot get github token from deployment secrets %s', ex)
        return self._token

    def tags(self) -> List[dict]:
        return [t for t in self._tags()]

    def get_tag(self, version) -> Optional[dict]:
        """Get specific tag by tag version"""

        req_url = urljoin(self._base_url, f'git/refs/tags/{version}')
        LOG.info('Get target tag from %s', req_url)
        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)
        response.raise_for_status()

        tag = response.json()
        tag_data = {'name': version,
                    'commit_id': tag['object']['sha']}
        return tag_data

    def latest_tag(self) -> Optional[dict]:
        """Github API will return the tags and sort descending
        here we get the 1st tag as latest tag
        """

        tags = self.tags()
        if tags:
            return tags[0]
        else:
            return None

    def create_tag(self, version: str, commit_id: str):
        """Create a git tag"""

        data = {
            'ref': f'refs/tags/{version}',
            'sha': commit_id
        }

        req_url = urljoin(self._base_url, 'git/refs')

        LOG.info('Create tag %s on %s from %s', version, commit_id, req_url)

        response = self._session.post(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def releases(self, release_id=None):
        """Get github releases"""

        req_url = urljoin(self._base_url, 'releases')
        if release_id:
            req_url = urljoin(req_url, release_id)

        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)

        releases = []
        for release in response.json():
            releases.append(release)

        return releases

    def create_release(self, tag: str, target: str, description=None, is_draft=False, is_prerelease=False):
        """Create Giyhub release on specific target.
        target could be a commit id or branch name
        """
        data = {
            'tag_name': tag,
            'target_commitish': target,
            'name': f'Version {tag}',
            'body': description or '',
            'draft': is_draft,
            'prerelease': is_prerelease
        }

        req_url = urljoin(self._base_url, 'releases')

        LOG.info('Create release %s on %s from %s', tag, target, req_url)

        response = self._session.post(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def edit_release(self, release_id: int, tag: str, description=None, is_draft=False, is_prerelease=False):
        """Create Giyhub release on specific target.
        target could be a commit id or branch name
        """
        data = {
            'tag_name': tag,
            'name': f'Version {tag}',
            'body': description or '',
            'draft': is_draft,
            'prerelease': is_prerelease
        }

        req_url = urljoin(self._base_url, f'releases/{release_id}')

        LOG.info('Edit release %s from %s', tag, req_url)

        response = self._session.patch(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def get_release_by_tag(self, tag: str):
        """Create Giyhub release on specific target.
        target could be a commit id or branch name
        """

        req_url = urljoin(self._base_url, f'releases/tags/{tag}')

        LOG.info('Get release by tag %s from %s', tag, req_url)

        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)

        response.raise_for_status()

        return response.json()

    def get_branch(self, branch_name: str):
        req_url = urljoin(self._base_url, f'branches/{branch_name}')

        LOG.info('Get branch %s from %s', branch_name, req_url)

        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)

        response.raise_for_status()

        return response.json()

    def get_branch_author(self, branch_name: str) -> str:
        branch_info = self.get_branch(branch_name)
        return branch_info['commit']['author']['login']

    def get_branch_sha(self, branch_name: str) -> str:
        branch_info = self.get_branch(branch_name)
        return branch_info['commit']['sha']

    def create_branch(self, branch_name: str, hash: str) -> str:
        """
        Creating new branch, if branch already exists, raise HTTP error 422
        """
        data = {
            "ref": f'refs/heads/{branch_name}',
         	"sha": hash
	    }

        req_url = urljoin(self._base_url, 'git/refs')

        LOG.info(f'Create branch {branch_name} base on sha {hash} from {req_url}')

        response = self._session.post(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def get_trees(self, tree_sha: str) -> str:
        
        req_url = urljoin(self._base_url, f'git/trees/{tree_sha}')
        
        response = self._session.get(req_url, headers=self._headers(), timeout=self._timeout_sec)

        response.raise_for_status()

        return response.json()

    def get_file_sha(self, tree_sha: str, file_name: str) -> str:
        trees_info = self.get_trees(tree_sha)
        for file_info in trees_info['tree']:
            print(file_info)
            if file_info['path'] == file_name:
                return file_info['sha']

    def create_file_contents(self, branch_name: str, path: str, file_hash: str, content: str) -> str:
        content_bytes = content.encode('ascii')
        base64_content_bytes = base64.b64encode(content_bytes)
        base64_content_string = base64_content_bytes.decode('ascii')

        data = {
            "message": f'auto added by jy bot at {int(time.time())}',
            "content": base64_content_string,
            "sha": file_hash,
            "branch": branch_name
        }

        req_url = urljoin(self._base_url, f'contents/{path}')

        response = self._session.put(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def create_pr(self, head_branch: str, base_branch: str) -> str:
        data = {
            "title": 'Automerging ' + head_branch + ' into ' + base_branch,
			"body": 'This pull request was created by the autom jy bot.',
            "head": head_branch,
            "base": base_branch,
        }

        req_url = urljoin(self._base_url, 'pulls')

        LOG.info(f'Create pr {head_branch} on base {base_branch} from {req_url}')

        response = self._session.post(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()

    def comment_pr(self, pr_number: int, commit_id: str, comment: str):
        """Comment a PR"""

        data = {
            'event': 'COMMENT',
            'body': comment,
            'commit_id': commit_id,
        }

        req_url = urljoin(self._base_url, f'pulls/{pr_number}/reviews')

        response = self._session.post(req_url, headers=self._headers(), json=data, timeout=self._timeout_sec)

        response.raise_for_status()
        return

    def close(self):
        if self._session:
            self._session.close()


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    ee = GitHubClient(repo='v1-hub-plugin', token=os.getenv('github_ee_token'))
    t = int(time.time())
    pr_branch = f'test-pipeline-{t}'
    master_branch = 'master'
    trigger_version = 'version.txt'
    content = f'v.1.0.207-{t}'
    
    master_sha = ee.get_branch_sha(master_branch)
    ee.create_branch(pr_branch, hash=master_sha)
    tree_sha = ee.get_branch_sha(pr_branch)
    file_sha = ee.get_file_sha(tree_sha=tree_sha, file_name=trigger_version)
    LOG.info(ee.create_file_contents(branch_name=pr_branch, path=trigger_version, file_hash=file_sha, content=content))
    ee.create_pr(pr_branch, 'master')