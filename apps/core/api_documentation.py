"""
API Documentation Generation
Postman collection export and SDK generation.
"""
import json
from typing import Dict, Any, List
from django.conf import settings


class PostmanCollectionGenerator:
    """
    Generate Postman collection from OpenAPI schema.
    """
    
    def generate_collection(
        self,
        base_url: str = 'http://localhost:8000',
        collection_name: str = 'HishamOS API'
    ) -> Dict[str, Any]:
        """
        Generate Postman collection.
        
        Args:
            base_url: Base URL for API
            collection_name: Collection name
        
        Returns:
            Postman collection dictionary
        """
        try:
            from drf_spectacular.views import SpectacularAPIView
            from django.test import RequestFactory
            from django.contrib.auth.models import AnonymousUser
            
            # Create a request to get the schema
            factory = RequestFactory()
            request = factory.get('/api/schema/')
            request.user = AnonymousUser()
            
            # Get OpenAPI schema
            schema_view = SpectacularAPIView.as_view()
            response = schema_view(request)
            
            # Get schema data
            if hasattr(response, 'data'):
                schema = response.data
            elif hasattr(response, 'render'):
                # If it's a rendered response, parse it
                import json
                schema = json.loads(response.content.decode('utf-8'))
            else:
                # Fallback: try to get from settings
                from drf_spectacular.settings import spectacular_settings
                schema = spectacular_settings.DEFAULT_GENERATOR_CLASS().get_schema(
                    request=request,
                    public=True
                )
        except Exception as e:
            # Fallback: return basic collection structure
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not generate full schema: {e}. Using basic structure.")
            schema = {'paths': {}}
        
        # Convert OpenAPI to Postman format
        collection = {
            'info': {
                'name': collection_name,
                'description': 'HishamOS API Collection',
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            'item': self._convert_paths_to_items(schema.get('paths', {}), base_url),
            'variable': [
                {
                    'key': 'base_url',
                    'value': base_url,
                    'type': 'string'
                },
                {
                    'key': 'token',
                    'value': '{{your_jwt_token}}',
                    'type': 'string'
                }
            ]
        }
        
        return collection
    
    def _convert_paths_to_items(self, paths: Dict[str, Any], base_url: str) -> List[Dict]:
        """Convert OpenAPI paths to Postman items."""
        items = []
        
        # Group by path prefix for better organization
        path_groups = {}
        
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
                
            # Extract path prefix (e.g., /api/v1/agents -> agents)
            path_parts = [p for p in path.split('/') if p and p != 'api' and p != 'v1']
            prefix = path_parts[0] if path_parts else 'root'
            
            if prefix not in path_groups:
                path_groups[prefix] = []
            
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete', 'options']:
                    if not isinstance(details, dict):
                        continue
                    
                    item = {
                        'name': details.get('summary', f'{method.upper()} {path}'),
                        'request': {
                            'method': method.upper(),
                            'header': self._convert_headers(details),
                            'url': {
                                'raw': f'{{{{base_url}}}}{path}',
                                'host': ['{{base_url}}'],
                                'path': [p for p in path.split('/') if p]  # All path segments
                            },
                            'body': self._convert_body(details),
                            'description': details.get('description', '')
                        },
                        'response': []
                    }
                    path_groups[prefix].append(item)
        
        # Organize into folders
        for prefix, group_items in path_groups.items():
            if len(group_items) > 1:
                # Create folder
                items.append({
                    'name': prefix.capitalize(),
                    'item': group_items
                })
            else:
                # Single item, add directly
                items.extend(group_items)
        
        return items
    
    def _convert_headers(self, details: Dict) -> List[Dict]:
        """Convert OpenAPI headers to Postman format."""
        headers = []
        
        # Add authentication header (most endpoints require auth)
        headers.append({
            'key': 'Authorization',
            'value': 'Bearer {{token}}',
            'type': 'text',
            'description': 'JWT authentication token'
        })
        
        # Add content type for POST/PUT/PATCH
        if 'requestBody' in details:
            headers.append({
                'key': 'Content-Type',
                'value': 'application/json',
                'type': 'text'
            })
        
        # Add Accept header
        headers.append({
            'key': 'Accept',
            'value': 'application/json',
            'type': 'text'
        })
        
        return headers
    
    def _convert_body(self, details: Dict) -> Dict:
        """Convert OpenAPI request body to Postman format."""
        if 'requestBody' not in details:
            return {}
        
        body = details['requestBody']
        content = body.get('content', {})
        
        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            example = self._generate_example_from_schema(schema)
            
            return {
                'mode': 'raw',
                'raw': json.dumps(example, indent=2),
                'options': {
                    'raw': {
                        'language': 'json'
                    }
                }
            }
        
        return {}
    
    def _generate_example_from_schema(self, schema: Dict) -> Dict:
        """Generate example from JSON schema."""
        example = {}
        
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                prop_type = prop_schema.get('type', 'string')
                
                if prop_type == 'string':
                    example[prop_name] = prop_schema.get('example', f'sample_{prop_name}')
                elif prop_type == 'integer':
                    example[prop_name] = prop_schema.get('example', 0)
                elif prop_type == 'boolean':
                    example[prop_name] = prop_schema.get('example', False)
                elif prop_type == 'array':
                    example[prop_name] = []
                else:
                    example[prop_name] = None
        
        return example
    
    def export_collection(
        self,
        output_path: str,
        base_url: str = 'http://localhost:8000'
    ) -> str:
        """
        Export Postman collection to file.
        
        Args:
            output_path: Output file path
            base_url: Base URL for API
        
        Returns:
            Path to exported file
        """
        collection = self.generate_collection(base_url)
        
        with open(output_path, 'w') as f:
            json.dump(collection, f, indent=2)
        
        return output_path


class PythonSDKGenerator:
    """
    Generate Python SDK from OpenAPI schema.
    """
    
    def generate_sdk(
        self,
        output_dir: str = 'sdk/python',
        package_name: str = 'hishamos_sdk'
    ) -> str:
        """
        Generate Python SDK.
        
        Args:
            output_dir: Output directory
            package_name: Package name
        
        Returns:
            Path to generated SDK
        """
        # This would generate a full Python SDK
        # For now, create a basic structure
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Create __init__.py
        init_content = f'''"""
{package_name} - Python SDK for HishamOS API
"""
__version__ = "1.0.0"
'''
        
        with open(f'{output_dir}/__init__.py', 'w') as f:
            f.write(init_content)
        
        # Create client.py
        client_content = '''"""
HishamOS API Client
"""
import requests
from typing import Optional, Dict, Any


class HishamOSClient:
    """Client for HishamOS API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_agents(self):
        """Get all agents."""
        return self._request('GET', '/api/v1/agents/')
    
    def create_agent(self, data: Dict[str, Any]):
        """Create an agent."""
        return self._request('POST', '/api/v1/agents/', json=data)
    
    # Add more methods as needed
'''
        
        with open(f'{output_dir}/client.py', 'w') as f:
            f.write(client_content)
        
        return output_dir


class JavaScriptSDKGenerator:
    """
    Generate JavaScript/TypeScript SDK from OpenAPI schema.
    """
    
    def generate_sdk(
        self,
        output_dir: str = 'sdk/javascript',
        package_name: str = '@hishamos/sdk'
    ) -> str:
        """
        Generate JavaScript SDK.
        
        Args:
            output_dir: Output directory
            package_name: Package name
        
        Returns:
            Path to generated SDK
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Create package.json
        package_json = {
            'name': package_name,
            'version': '1.0.0',
            'description': 'HishamOS API SDK',
            'main': 'index.js',
            'types': 'index.d.ts',
            'scripts': {
                'build': 'tsc'
            },
            'dependencies': {
                'axios': '^1.6.0'
            },
            'devDependencies': {
                'typescript': '^5.0.0',
                '@types/node': '^20.0.0'
            }
        }
        
        with open(f'{output_dir}/package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create index.ts
        index_ts = '''/**
 * HishamOS API SDK
 */
import axios, { AxiosInstance } from 'axios';

export interface HishamOSClientConfig {
  baseUrl: string;
  apiKey?: string;
}

export class HishamOSClient {
  private client: AxiosInstance;

  constructor(config: HishamOSClientConfig) {
    this.client = axios.create({
      baseURL: config.baseUrl,
      headers: config.apiKey
        ? { Authorization: `Bearer ${config.apiKey}` }
        : {},
    });
  }

  async getAgents() {
    const response = await this.client.get('/api/v1/agents/');
    return response.data;
  }

  async createAgent(data: any) {
    const response = await this.client.post('/api/v1/agents/', data);
    return response.data;
  }

  // Add more methods as needed
}

export default HishamOSClient;
'''
        
        with open(f'{output_dir}/index.ts', 'w') as f:
            f.write(index_ts)
        
        return output_dir


# Global instances
_postman_generator = None
_python_sdk_generator = None
_js_sdk_generator = None


def get_postman_generator() -> PostmanCollectionGenerator:
    """Get or create Postman generator instance."""
    global _postman_generator
    if _postman_generator is None:
        _postman_generator = PostmanCollectionGenerator()
    return _postman_generator


def get_python_sdk_generator() -> PythonSDKGenerator:
    """Get or create Python SDK generator instance."""
    global _python_sdk_generator
    if _python_sdk_generator is None:
        _python_sdk_generator = PythonSDKGenerator()
    return _python_sdk_generator


def get_js_sdk_generator() -> JavaScriptSDKGenerator:
    """Get or create JavaScript SDK generator instance."""
    global _js_sdk_generator
    if _js_sdk_generator is None:
        _js_sdk_generator = JavaScriptSDKGenerator()
    return _js_sdk_generator

