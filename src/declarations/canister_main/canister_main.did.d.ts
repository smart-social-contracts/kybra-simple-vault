import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface CallbackStrategy {
  'token' : Token,
  'callback' : [Principal, string],
}
export interface HttpRequest {
  'url' : string,
  'method' : string,
  'body' : Uint8Array | number[],
  'headers' : Array<[string, string]>,
}
export interface HttpResponse {
  'body' : Uint8Array | number[],
  'headers' : Array<[string, string]>,
  'upgrade' : [] | [boolean],
  'streaming_strategy' : [] | [StreamingStrategy],
  'status_code' : number,
}
export interface StreamingCallbackHttpResponse {
  'token' : [] | [Token],
  'body' : Uint8Array | number[],
}
export type StreamingStrategy = { 'Callback' : CallbackStrategy };
export interface Token { 'key' : string }
export interface _SERVICE {
  'caller' : ActorMethod<[], Principal>,
  'create_user' : ActorMethod<[string], string>,
  'create_user_endpoint' : ActorMethod<[], string>,
  'destroy_universe' : ActorMethod<[], string>,
  'do_request' : ActorMethod<[string], string>,
  'get_canister_balance' : ActorMethod<[], bigint>,
  'get_organization_data' : ActorMethod<[string], string>,
  'get_organization_list' : ActorMethod<[], string>,
  'get_proposal_data' : ActorMethod<[string], string>,
  'get_stats' : ActorMethod<[], string>,
  'get_token_data' : ActorMethod<[string], string>,
  'get_token_list' : ActorMethod<[], string>,
  'get_token_transactions' : ActorMethod<[string, string, bigint], string>,
  'get_universe' : ActorMethod<[], string>,
  'get_user_data' : ActorMethod<[string], string>,
  'get_user_list' : ActorMethod<[], string>,
  'greet' : ActorMethod<[string], string>,
  'http_request' : ActorMethod<[HttpRequest], HttpResponse>,
  'run_code' : ActorMethod<[string], string>,
  'user_join_organization_endpoint' : ActorMethod<[string], string>,
}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
