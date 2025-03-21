"""Test data artifacts for canister main tests"""
from ggg.utils import IGNORE_TAG

# Token test data
DEFAULT_TOKEN = {
    'balances': IGNORE_TAG,
    'creator': IGNORE_TAG,
    'extension_code': ['ExtensionCode@DEFAULT_EXTENSION_CODE_TOKEN'],
    'id': 'BTC',
    'metadata': {},
    'name': 'Bitcoin',
    'owner': IGNORE_TAG,
    'timestamp_created': IGNORE_TAG,
    'timestamp_updated': IGNORE_TAG,
    'type': 'Token',
    'updater': IGNORE_TAG
}

# Organization token template


def create_org_token(org_name):
    """Create a token for an organization"""
    return {
        'balances': IGNORE_TAG,
        'creator': IGNORE_TAG,
        'extension_code': ['ExtensionCode@DEFAULT_EXTENSION_CODE_TOKEN'],
        'id': f'ORG_{org_name}',
        'metadata': {},
        'name': f'organization_{org_name}',
        'organization': [f'Organization@{org_name}'],
        'owner': IGNORE_TAG,
        'timestamp_created': IGNORE_TAG,
        'timestamp_updated': IGNORE_TAG,
        'type': 'Token',
        'updater': IGNORE_TAG
    }


# Land token test data
LAND_TOKEN = {
    'balances': IGNORE_TAG,
    'creator': IGNORE_TAG,
    'extension_code': ['ExtensionCode@DEFAULT_EXTENSION_CODE_TOKEN'],
    'id': 'LAND_CH',
    'land': IGNORE_TAG,  # ['Land@Switzerland'], TODO
    'metadata': {},
    'name': IGNORE_TAG,  # 'Land Ownership Token', TODO
    'owner': IGNORE_TAG,
    'timestamp_created': IGNORE_TAG,
    'timestamp_updated': IGNORE_TAG,
    'type': 'LandToken',
    'updater': IGNORE_TAG
}

# All tokens in the system
ALL_TOKENS = [
    DEFAULT_TOKEN,
    LAND_TOKEN,
    create_org_token('state'),
    create_org_token('Congress'),
    create_org_token('Government'),
    create_org_token('Supreme Court'),
    create_org_token('Ministry of Economy'),
    create_org_token('Ministry of Security'),
    create_org_token('Ministry of Education'),
    create_org_token('Tax Department'),
    create_org_token('Police Department'),
    create_org_token('School Department')
]

# Initial universe test data
INITIAL_UNIVERSE = {
    'extensions': [
        {
            'creator': IGNORE_TAG,
            'id': 'DEFAULT_EXTENSION_CODE_ORGANIZATION',
            'owner': IGNORE_TAG,
            'source_code': "<IGNORE>",
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'ExtensionCode',
            'updater': IGNORE_TAG
        },
        {
            'creator': IGNORE_TAG,
            'id': 'DEFAULT_EXTENSION_CODE_TOKEN',
            'owner': IGNORE_TAG,
            'source_code': "<IGNORE>",
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'tokens': ['Token@BTC'],
            'type': 'ExtensionCode',
            'updater': IGNORE_TAG
        }
    ],
    'organizations': [],
    'tokens': [DEFAULT_TOKEN],
    'user_groups': [],
    'users': [
        {
            'creator': IGNORE_TAG,
            'id': 'DEFAULT',
            'owner': IGNORE_TAG,
            'principal': 'aaa-0',
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'User',
            'updater': IGNORE_TAG,
            'wallet': ['Wallet@0']
        }
    ]
}

# Final universe test data after running extension code
FINAL_UNIVERSE = {
    'extensions': [
        {
            'creator': IGNORE_TAG,
            'id': 'DEFAULT_EXTENSION_CODE_ORGANIZATION',
            'owner': IGNORE_TAG,
            'source_code': "<IGNORE>",
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'ExtensionCode',
            'updater': IGNORE_TAG,
            'organizations': IGNORE_TAG,
        },
        {
            'creator': IGNORE_TAG,
            'id': 'DEFAULT_EXTENSION_CODE_TOKEN',
            'owner': IGNORE_TAG,
            'source_code': "<IGNORE>",
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'tokens': ['Token@BTC'],
            'type': 'ExtensionCode',
            'updater': IGNORE_TAG,
            'tokens': IGNORE_TAG,
        },    
        {
            'creator': IGNORE_TAG,
            'id': IGNORE_TAG,
            'owner': IGNORE_TAG,
            'proposal': IGNORE_TAG,
            'source_code': IGNORE_TAG,
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'ExtensionCode',
            'updater': IGNORE_TAG,
            'proposal': IGNORE_TAG,
        }
    ],
    'organizations': [
        {
            'creator': IGNORE_TAG,
            'id': org_name,
            'owner': IGNORE_TAG,
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'Organization',
            'updater': IGNORE_TAG,
            'token': [f'Token@ORG_{org_name}']
        }
        for org_name in [
            'state', 'Congress', 'Government', 'Supreme Court',
            'Ministry of Economy', 'Ministry of Security', 'Ministry of Education',
            'Tax Department', 'Police Department', 'School Department'
        ]
    ],
    'tokens': ALL_TOKENS,
    'user_groups': [],
    'users': [
        {
            'creator': IGNORE_TAG,
            'id': user_id,
            'owner': IGNORE_TAG,
            'principal': principal,
            'timestamp_created': IGNORE_TAG,
            'timestamp_updated': IGNORE_TAG,
            'type': 'User',
            'updater': IGNORE_TAG,
            'wallet': ['Wallet@0'] if user_id == 'DEFAULT' else [f'Wallet@{user_id.lower()}']
        }
        for user_id, principal in [('DEFAULT', 'aaa-0'), ('Alice', 'alice_identity'), ('Bob', 'bob_identity')]
    ]
}

# Run code test data
RUN_CODE_RESPONSE = {'output': 'OK', 'status': 'success'}

# Error responses
TOKEN_NOT_FOUND_ERROR = {"error": "Token not found"}
