# """Tests for entity functionality in Kybra Simple DB."""

import ast

from tester import Tester

from utils import parse_candid
# from logger import get_logger
# log = get_logger()


class TestCandid:
    def test_parse_candid_message_archived(self):

        i = '''
(
  {
    1779015299: 2337000 
    2799807105: 2338698 
    3331539157:  {}
    3650848786:  {
      {
        2131139013: func "nbsys-saaaa-aaaar-qaaga-cai".gettransactions
        2215343202: 0 
        2668074214: 1 
      }
    }
  },
)
      '''

        d = {'first_index': 2337000,
             'log_length': 2338698,
             'transactions': [], 'archived_transactions': {}}

        if parse_candid(i) == d:
            return 0
        return 1

    def test_parse_candid(self):
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

        d = {'first_index': 2328390,
             'log_length': 2328398,
             'transactions': [
                 {1092621391: None,
                  'kind': 'transfer',
                  1214008994: None,
                  1378506061: None,
                  'timestamp': 1742840332822818232,
                  'transfer': {
                      'to': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                      'from': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                      1213809850: None,
                      3258775938: None,
                      'amount': 908977,
                      3868658507: None}},
                 {1092621391: None,
                  'kind': 'transfer',
                  1214008994: None,
                  1378506061: None,
                  'timestamp': 1742840334069599178,
                  'transfer': {
                      'to': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                      'from': {'owner': 'ztwhb-qiaaa-aaaaj-azw7a-cai'},
                      1213809850: None,
                      3258775938: None,
                      'amount': 447890,
                      3868658507: None}},
                 {1092621391: None,
                  'kind': 'transfer',
                  1214008994: None,
                  1378506061: None,
                  'timestamp': 1742840639059074036,
                  'transfer': {
                      'to': {'owner': 'rtpxn-77ite-cm6ta-qh5te-pdqj6-ugxwe-dncpt-ewp7c-nui4j-cpvwp-oae'},
                      'from': {'owner': 'xmiu5-jqaaa-aaaag-qbz7q-cai'},
                      1213809850: '\x05\x068',
                      3258775938: None,
                      'amount': 1236274,
                      3868658507: None}}
             ], 'archived_transactions': {}}

        if parse_candid(i) == d:
            return 0
        return 1


def run():
    print("Running tests...")
    tester = Tester(TestCandid)
    return tester.run_tests(['test_parse_candid_message_archived'])


if __name__ == "__main__":
    exit(run())
