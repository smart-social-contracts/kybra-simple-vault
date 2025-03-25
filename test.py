import ast


i = '''
(
  record {
    1_779_015_299 = 2_328_390 : nat;
    2_799_807_105 = 2_328_398 : nat;
    3_331_539_157 = vec {
      record {
        1_092_621_391 = null;
        1_191_829_844 = "transfer";
        1_214_008_994 = null;
        1_378_506_061 = null;
        2_781_795_542 = 1_742_840_332_822_818_232 : nat64;
        3_664_621_355 = opt record {
          25_979 = record {
            947_296_307 = principal "ztwhb-qiaaa-aaaaj-azw7a-cai";
            1_349_681_965 = null;
          };
          5_094_982 = opt (10 : nat);
          1_136_829_802 = record {
            947_296_307 = principal "ztwhb-qiaaa-aaaaj-azw7a-cai";
            1_349_681_965 = opt blob "\00\00\00\ea\8f\40\10\53\90\96\01\82\0d\d6\ff\ee\cc\f7\fb\ea\85\d8\6d\fb\75\97\03\43\55\2c\50\02";
          };
          1_213_809_850 = null;
          3_258_775_938 = null;
          3_573_748_184 = 908_977 : nat;
          3_868_658_507 = null;
        };
      };
      record {
        1_092_621_391 = null;
        1_191_829_844 = "transfer";
        1_214_008_994 = null;
        1_378_506_061 = null;
        2_781_795_542 = 1_742_840_334_069_599_178 : nat64;
        3_664_621_355 = opt record {
          25_979 = record {
            947_296_307 = principal "ztwhb-qiaaa-aaaaj-azw7a-cai";
            1_349_681_965 = null;
          };
          5_094_982 = opt (10 : nat);
          1_136_829_802 = record {
            947_296_307 = principal "ztwhb-qiaaa-aaaaj-azw7a-cai";
            1_349_681_965 = opt blob "\00\00\00\b6\37\f9\73\e5\b9\96\e6\6e\53\79\7c\16\77\c0\93\bc\ff\44\09\dd\1b\31\18\94\4a\4f\48\02";
          };
          1_213_809_850 = null;
          3_258_775_938 = null;
          3_573_748_184 = 447_890 : nat;
          3_868_658_507 = null;
        };
      };
      record {
        1_092_621_391 = null;
        1_191_829_844 = "transfer";
        1_214_008_994 = null;
        1_378_506_061 = null;
        2_781_795_542 = 1_742_840_639_059_074_036 : nat64;
        3_664_621_355 = opt record {
          25_979 = record {
            947_296_307 = principal "rtpxn-77ite-cm6ta-qh5te-pdqj6-ugxwe-dncpt-ewp7c-nui4j-cpvwp-oae";
            1_349_681_965 = null;
          };
          5_094_982 = opt (10 : nat);
          1_136_829_802 = record {
            947_296_307 = principal "xmiu5-jqaaa-aaaag-qbz7q-cai";
            1_349_681_965 = null;
          };
          1_213_809_850 = opt blob "\00\00\00\00\00\05\68\73";
          3_258_775_938 = null;
          3_573_748_184 = 1_236_274 : nat;
          3_868_658_507 = null;
        };
      };
    };
    3_650_848_786 = vec {};
  },
)
'''



i = i.strip()
i = i.replace('record {', '{')
i = i.replace('opt', '')
i = i.replace('blob', '')
i = i.replace('vec', '')
i = i.replace('principal', '')
i = i.replace('null', '"None"')
i = i.replace(': nat64', '')
i = i.replace(': nat', '')
i = i.replace(';', '')
i = i.replace('_', '')
i = i.replace(' = ', ': ')
i = i.replace('\x00', '')

i2 = []
is_inside_transactions = False
level = 0
lines = i.split('\n')
for i, l in enumerate(lines):
    # l = l.strip()
    # print(level, l)

    if is_inside_transactions:
        if '{' in l:
            level += 1
        if '}' in l:
            level -= 1
            if level < 0:
                is_inside_transactions = False
                l = ']'

    if '1349681965' in l:
        continue
    if '5094982' in l:
        continue
    if l == '}' and is_inside_transaction:
        l = ']'
    if '{' not in l and '(' not in l:
        if ',' not in l and i != len(lines) - 1:
            l += ','
    if '3331539157:  {' in l:
        l = '3331539157 : ['
        is_inside_transactions = True
        level = 0

    i2.append(l)


i2 = '\n'.join(i2)


field_map = {
    "1_779_015_299": "first_index",
    "2_799_807_105": "log_length",
    "3_331_539_157": "transactions",
    "3_650_848_786": "archived_transactions",
    "2_131_139_013": "callback",
    "2_215_343_202": "start",
    "2_668_074_214": "length"
}

for k, v in field_map.items():
    i2 = i2.replace(k.replace('_', ''), '"%s"' % v)

print(i2)
d = ast.literal_eval(i2)


from pprint import pprint
pprint(d)
