# FortiManager API Refactoring Summary

This document summarizes the comprehensive refactoring of the FortiManager API client to comply with the official FortiManager JSON-RPC API documentation (https://how-to-fortimanager-api.readthedocs.io/en/latest/001_fmg_json_api_introduction.html).

## Issues Found and Fixed

### 1. JSON-RPC Format Compliance (CRITICAL)

**Issue**: The original `JsonRpcMixin.build_json_rpc_request` method was using an incorrect JSON-RPC format with `params` as an object instead of an array.

**Original (Incorrect)**:
```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "get",
  "params": {
    "url": "/sys/status",
    "verbose": 0
  }
}
```

**Fixed (Official Format)**:
```json
{
  "id": 1,
  "method": "get",
  "params": [
    {
      "url": "/sys/status",
      "verbose": 0
    }
  ],
  "session": "session_id"
}
```

**Changes Made**:
- Modified `JsonRpcMixin.build_json_rpc_request()` to use array format for `params`
- Removed invalid `jsonrpc: "2.0"` field (FortiManager doesn't use this)
- Updated `JsonRpcMixin.parse_json_rpc_response()` to handle FortiManager-specific response format

### 2. URL Structure Corrections

**Issue**: Some API endpoints were using incorrect URL structures that don't match the official documentation.

**Official URL Patterns**:
- Device Global Settings: `/pm/config/device/<device>/global/<cli>`
- Device VDOM Settings: `/pm/config/device/<device>/vdom/<vdom>/<cli>`
- Policy Package: `/pm/config/adom/<adom>/pkg/<package>/<cli>`
- ADOM Management: `/dvmdb/adom`

**Changes Made**:

1. **Firewall Policies**: 
   - Fixed `get_firewall_policies()` to use device-centric URL: 
     `/pm/config/device/{device}/vdom/{vdom}/firewall/policy`
   - Previously used package-centric URL incorrectly

2. **Policy Management**:
   - Updated `create_firewall_policy()`, `update_firewall_policy()`, `delete_firewall_policy()` to use device-centric URLs
   - Added `get_package_policies()` for package-level policy management

3. **Device Settings vs Security Settings Separation**:
   - Added `get_device_global_settings()` for device global configuration
   - Added `get_device_vdom_settings()` for VDOM-specific security settings
   - Added `get_policy_package_settings()` for ADOM-level policy packages

### 3. Packet Path Analysis Enhancement

**Issue**: Packet path analysis was using mock data or basic path tracing without proper FortiManager API integration.

**Changes Made**:
- Added comprehensive `analyze_packet_path()` method to FortiManagerAPIClient
- Integrates real FortiManager APIs for:
  - Routing table analysis (`get_routes()`)
  - Interface configuration (`get_interfaces()`)  
  - Firewall policy evaluation (`get_firewall_policies()`)
- Performs actual packet path analysis through FortiGate devices
- Updates route handler to use real FortiManager APIs in production mode

### 4. Authentication Improvements

**Verified Support For**:
- Session-based authentication (username/password)
- Token-based authentication (API tokens)
- Proper session management and logout
- Authentication error handling and retry logic

### 5. Device Settings vs Security Settings Management

**Added Clear Separation**:

1. **Device Settings** (Global Configuration):
   ```python
   client.get_device_global_settings("FGT-001", "system/interface")
   client.set_device_global_settings("FGT-001", "system/dns", data)
   ```

2. **Security Settings** (VDOM Configuration):
   ```python
   client.get_device_vdom_settings("FGT-001", "root", "firewall/policy")  
   client.set_device_vdom_settings("FGT-001", "root", "router/static", data)
   ```

3. **Policy Package Management** (ADOM Level):
   ```python
   client.get_policy_package_settings("default", "firewall/address")
   ```

## API Method Updates

### Core Methods Fixed:
- `get_firewall_policies()` - Now uses device-centric URL
- `create_firewall_policy()` - Device settings approach
- `update_firewall_policy()` - Device settings approach  
- `delete_firewall_policy()` - Device settings approach

### New Methods Added:
- `get_package_policies()` - Policy package management
- `analyze_packet_path()` - Real FortiManager-based packet analysis
- `get_device_global_settings()` - Device global configuration
- `set_device_global_settings()` - Device global configuration
- `get_device_vdom_settings()` - VDOM security settings
- `set_device_vdom_settings()` - VDOM security settings
- `get_policy_package_settings()` - ADOM policy packages

## Testing and Validation

Created comprehensive test suite (`tests/test_fortimanager_api_refactored.py`) covering:

1. **JSON-RPC Format Compliance**: Validates request/response format matches official standard
2. **URL Structure Validation**: Ensures all endpoints use correct URL patterns
3. **Authentication Flows**: Tests both session and token-based authentication
4. **Packet Path Analysis**: Integration testing for path analysis functionality
5. **Device vs Package Settings**: Validates proper separation of concerns

## Route Handler Updates

Updated `src/routes/fortimanager_routes.py`:
- `/analyze-packet-path` endpoint now uses real FortiManager APIs in production
- Maintains mock data support for testing
- Proper error handling and authentication

## Compliance Verification

The refactored implementation now fully complies with:

1. **FortiManager JSON-RPC API Standard**: 
   - Correct request format with `params` array
   - Proper response parsing with status code handling
   - Session management as per official documentation

2. **Official URL Structures**:
   - Device configuration: `/pm/config/device/<device>/global/<cli>`
   - VDOM settings: `/pm/config/device/<device>/vdom/<vdom>/<cli>`
   - Policy packages: `/pm/config/adom/<adom>/pkg/<package>/<cli>`

3. **Authentication Methods**:
   - Session-based: Login with username/password, get session ID
   - Token-based: Use pre-generated API tokens with Bearer authorization

4. **Best Practices**:
   - Proper error handling and response parsing
   - Clear separation between device and security settings
   - Comprehensive packet path analysis using multiple API calls

## Migration Notes

**Breaking Changes**:
- `build_json_rpc_request()` now returns different payload structure (params as array)
- Some URL patterns have changed for policy management methods
- Authentication flow may differ slightly due to improved error handling

**Backward Compatibility**:
- All existing method signatures remain the same
- Mock mode continues to work for testing
- Configuration loading unchanged

## Benefits

1. **Standards Compliance**: Full adherence to official FortiManager API documentation
2. **Improved Reliability**: Proper error handling and response parsing
3. **Enhanced Functionality**: Real packet path analysis capabilities
4. **Better Architecture**: Clear separation between device and security settings
5. **Future-Proof**: Easier to maintain and extend with new FortiManager features

This refactoring ensures the FortiGate Nextrade platform can reliably integrate with FortiManager devices using the official API standards, providing robust network monitoring and policy management capabilities.