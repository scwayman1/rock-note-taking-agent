"""Regenerate portable contracts from a single strict structural definition."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def array(item): return {'type': 'array', 'items': item}


def main():
    string = {'type': 'string', 'minLength': 1, 'maxLength': 20000}
    ident = {'type': 'string', 'pattern': '^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$'}
    timestamp = {'type': 'string', 'format': 'date-time'}
    boolean = {'type': 'boolean'}
    ref = obj({'source_id': ident, 'utterance_id': ident, 'quote': string})
    refs = array(ref); refs_required = dict(refs, minItems=1)
    utterance = obj({'id': ident, 'start': timestamp, 'end': timestamp, 'speaker': string, 'text': string, 'uncertainty': array(string)})
    source = obj({'id': ident, 'label': string, 'utterances': dict(array(utterance), minItems=1, maxItems=5000)})
    evidence = obj({'schema_version': {'type': 'string', 'enum': ['0.1']}, 'meeting_id': ident, 'title': string,
                    'start': timestamp, 'end': timestamp, 'boundary_reviewed': {'type': 'boolean', 'enum': [True]},
                    'adjacent_sources_checked': {'type': 'boolean', 'enum': [True]}, 'exclusions': array(string),
                    'gaps': array(obj({'start': timestamp, 'end': timestamp, 'reason': string})),
                    'sources': dict(array(source), minItems=1, maxItems=100)})
    kinds = ['ratified_decision', 'apparent_agreement', 'aligned_direction', 'proposal', 'reported_current', 'context', 'committed_action', 'editorial_action', 'open_question']
    draft = obj({'schema_version': {'type': 'string', 'enum': ['0.1']}, 'meeting_id': ident, 'edition': {'type': 'integer', 'minimum': 1, 'maximum': 999999},
                 'summary': array(obj({'id': ident, 'text': string, 'refs': refs_required})),
                 'items': array(obj({'id': ident, 'kind': {'type': 'string', 'enum': kinds}, 'text': string, 'owner': string, 'deadline': string,
                                    'refs': refs_required, 'owner_refs': refs, 'deadline_refs': refs})),
                 'caveats': array(string), 'review': obj({'evidence_reviewed': boolean, 'release_approved': boolean, 'reviewer': string, 'approved_at': string})})
    ingest_request = obj({'evidence': evidence})
    draft_request = obj({'evidence': evidence, 'draft': draft})
    requests = {'ingest': ingest_request, 'validate': draft_request, 'render': draft_request}
    descriptions = {'ingest': 'Validate bounded canonical meeting evidence and return source hashes. No model synthesis. HTTP hashes cover supplied JSON after canonical serialization, not original upstream export bytes.',
                    'validate': 'Validate draft structure and exact evidence anchors; does not verify semantic entailment, authority or consent.',
                    'render': 'Render restricted DRAFT HTML and non-activated actions CSV only; never publish, send or authorize release.'}
    source_manifest = obj({'schema_version': string, 'input_sha256': string, 'canonical_sha256': string,
                           'sources': array(obj({'source_id': string, 'canonical_sha256': string, 'utterance_count': {'type': 'integer'}})), 'limitations': string})
    responses = {'ingest': obj({'evidence': evidence, 'manifest': source_manifest}),
                 'validate': obj({'valid': boolean, 'semantic_review_required': boolean, 'publication_performed': boolean}),
                 'render': obj({'status': string, 'html': {'type': 'string'}, 'actions_csv': {'type': 'string'}})}
    def write(path, value):
        path = ROOT/path; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2)+'\n')
    for name, schema in [('evidence', evidence), ('draft', draft)]:
        write(Path('schemas')/(name+'.schema.json'), dict(schema, **{'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'Rock '+name+' 0.1'}))
    swagger = {'swagger': '2.0', 'info': {'title': 'Rock Note Taking Agent — preview-only local contract', 'version': '0.1.0'},
               'host': '127.0.0.1:8765', 'basePath': '/', 'schemes': ['http'], 'consumes': ['application/json'], 'produces': ['application/json'],
               'securityDefinitions': {'BearerToken': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header', 'description': 'Local only: full value Bearer <token>. Hosted deployment requires separately implemented identity and authorization.'}},
               'security': [{'BearerToken': []}], 'paths': {}}
    for name in requests:
        swagger['paths']['/'+name] = {'post': {'operationId': 'rock_'+name, 'summary': 'Rock '+name, 'description': descriptions[name],
            'parameters': [{'name': 'body', 'in': 'body', 'required': True, 'schema': requests[name]}],
            'responses': {'200': {'description': 'Validated result', 'schema': responses[name]}, '400': {'description': 'Invalid request'}, '401': {'description': 'Unauthorized'}, '413': {'description': 'Body exceeds 1 MiB'}}}}
    write(Path('adapters/copilot/openapi-v2.json'), swagger)
    write(Path('adapters/openai/tools.json'), [{'type': 'function', 'name': 'rock_'+name, 'description': descriptions[name], 'strict': True, 'parameters': requests[name]} for name in requests])


if __name__ == '__main__': main()
