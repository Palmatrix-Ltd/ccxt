const errorHierarchy = {
    'BaseError': {
        'ExchangeError': {
            'AuthenticationError': {
                'PermissionDenied': {
                    'AccountNotEnabled': {},
                },
                'AccountSuspended': {},
            },
            'ArgumentsRequired': {},
            'BadRequest': {
                'BadSymbol': {},
                'MarginModeAlreadySet': {},
                'NoChange': {},
                'OperationFailed': {},
            },
            'BadResponse': {
                'NullResponse': {},
                'ApiEngineFailed': {},
            },
            'InsufficientFunds': {},
            'InvalidAddress': {
                'AddressPending': {},
            },
            'InvalidOrder': {
                'OrderNotFound': {},
                'OrderNotCached': {},
                'CancelPending': {},
                'OrderImmediatelyFillable': {},
                'OrderNotFillable': {},
                'DuplicateOrderId': {},
                'ContractUnavailable': {},
            },
            'NotSupported': {},
        },
        'NetworkError': {
            'DDoSProtection': {
                'RateLimitExceeded': {},
            },
            'ExchangeNotAvailable': {
                'OnMaintenance': {},
            },
            'InvalidNonce': {},
            'RequestTimeout': {},
        },
    },
};

export default errorHierarchy;
