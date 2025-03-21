export const idlFactory = ({ IDL }) => {
  const HttpRequest = IDL.Record({
    'url' : IDL.Text,
    'method' : IDL.Text,
    'body' : IDL.Vec(IDL.Nat8),
    'headers' : IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text)),
  });
  const Token = IDL.Record({ 'key' : IDL.Text });
  const StreamingCallbackHttpResponse = IDL.Record({
    'token' : IDL.Opt(Token),
    'body' : IDL.Vec(IDL.Nat8),
  });
  const CallbackStrategy = IDL.Record({
    'token' : Token,
    'callback' : IDL.Func([Token], [StreamingCallbackHttpResponse], ['query']),
  });
  const StreamingStrategy = IDL.Variant({ 'Callback' : CallbackStrategy });
  const HttpResponse = IDL.Record({
    'body' : IDL.Vec(IDL.Nat8),
    'headers' : IDL.Vec(IDL.Tuple(IDL.Text, IDL.Text)),
    'upgrade' : IDL.Opt(IDL.Bool),
    'streaming_strategy' : IDL.Opt(StreamingStrategy),
    'status_code' : IDL.Nat16,
  });
  return IDL.Service({
    'caller' : IDL.Func([], [IDL.Principal], ['query']),
    'create_user' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'create_user_endpoint' : IDL.Func([], [IDL.Text], []),
    'destroy_universe' : IDL.Func([], [IDL.Text], []),
    'do_request' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_canister_balance' : IDL.Func([], [IDL.Nat], ['query']),
    'get_organization_data' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_organization_list' : IDL.Func([], [IDL.Text], ['query']),
    'get_proposal_data' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_stats' : IDL.Func([], [IDL.Text], ['query']),
    'get_token_data' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_token_list' : IDL.Func([], [IDL.Text], ['query']),
    'get_token_transactions' : IDL.Func(
        [IDL.Text, IDL.Text, IDL.Int],
        [IDL.Text],
        ['query'],
      ),
    'get_universe' : IDL.Func([], [IDL.Text], ['query']),
    'get_user_data' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'get_user_list' : IDL.Func([], [IDL.Text], ['query']),
    'greet' : IDL.Func([IDL.Text], [IDL.Text], ['query']),
    'http_request' : IDL.Func([HttpRequest], [HttpResponse], ['query']),
    'run_code' : IDL.Func([IDL.Text], [IDL.Text], []),
    'user_join_organization_endpoint' : IDL.Func([IDL.Text], [IDL.Text], []),
  });
};
export const init = ({ IDL }) => { return []; };
