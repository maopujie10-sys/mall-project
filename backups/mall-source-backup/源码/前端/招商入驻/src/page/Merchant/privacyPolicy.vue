<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('policy_title')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <div class="title">{{ $t("policy_tit") }}</div>
            <p>
              {{ $t("policy_titinfo", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_titinfo1") }}
            </p>
            <p>
              {{ $t("policy_titinfo2") }}
            </p>
            <p>
              {{ $t("policy_titinfo3") }}
            </p>
            <p>{{ $t("policy_titinfo4") }}</p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit2", { name: itemname }) }}</h2>
            <p>{{ $t("policy_tit2infot") }}</p>
            <ul>
              <li>{{ $t("policy_tit2info1") }}</li>
              <li>{{ $t("policy_tit2info1li") }}</li>
              <li>
                {{ $t("policy_tit2info1li1") }}
              </li>
              <li>
                {{ $t("policy_tit2info1li2") }}
              </li>
              <li>
                {{ $t("policy_tit2info1li3") }}
              </li>
              <li>
                {{ $t("policy_tit2info1li4") }}
              </li>
              <li>
                {{ $t("policy_tit2info1li5", { name: itemname }) }}
              </li>
              <!-- <li>{{ $t("policy_tit2info1li6") }};</li>
              <li>{{ $t("policy_tit2info1li7") }};</li>
              <li>{{ $t("policy_tit2info1li8") }}</li>
              <li>{{ $t("policy_tit2info1li9") }}</li> -->

              <p>
                {{ $t("policy_tit2info1li0") }}
              </p>
            </ul>
            <p>
              {{ $t("policy_tit2info2") }}
            </p>
            <p>
              {{ $t("policy_tit2info3") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit3", { name: itemname }) }}</h2>
            <p>{{ $t("policy_tit3info1", { name: itemname }) }}</p>
            <ul>
              <li>{{ $t("policy_tit3info1li1") }}</li>
              <li>{{ $t("policy_tit3info1li2") }}</li>
              <li>{{ $t("policy_tit3info1li3") }}</li>
              <li>{{ $t("policy_tit3info1li4") }}</li>
              <li>{{ $t("policy_tit3info1li5") }}</li>
              <li>{{ $t("policy_tit3info1li6") }}</li>
              <li>{{ $t("policy_tit3info1li7") }}</li>
              <li>{{ $t("policy_tit3info1li8") }}</li>
              <li>{{ $t("policy_tit3info1li9") }}</li>
              <li>{{ $t("policy_tit3info1li10") }}</li>
              <li>
                {{ $t("policy_tit3info1li11") }}
              </li>
              <li>
                {{ $t("policy_tit3info1li12") }}
              </li>
              <li>
                {{ $t("policy_tit3info1li13") }}
              </li>
              <!-- <li>{{ $t("policy_tit3info1li14") }}</li>
              <li>
                {{ $t("policy_tit3info1li15") }}
              </li>
              <li>{{ $t("policy_tit3info1li16") }}</li> -->
            </ul>
            <p>
              {{ $t("policy_tit3info2") }}
            </p>
            <p>
              {{ $t("policy_tit3info3", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit3info4") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit4") }}</h2>
            <p>
              {{ $t("policy_tit4info1") }}
            </p>
            <p>
              {{ $t("policy_tit4info2") }}
            </p>
            <p>
              {{ $t("policy_tit4info3") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit5") }}</h2>
            <p>
              {{ $t("policy_tit5info1") }}
            </p>
            <p>{{ $t("policy_tit5info2") }}</p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit6") }}</h2>
            <p>
              {{ $t("policy_tit6info1") }}
            </p>
            <ul>
              <li>
                {{ $t("policy_tit6info1info1") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info2", { name }) }}
              </li>
              <li>
                {{ $t("policy_tit6info1info3") }}
              </li>
              <li>{{ $t("policy_tit6info1info4") }}</li>
              <li>{{ $t("policy_tit6info1info5") }}</li>
              <li>{{ $t("policy_tit6info1info6") }}</li>
              <li>
                {{ $t("policy_tit6info1info7") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info8") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info9") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info10") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info11") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info12") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info13", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit6info1info14", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit6info1info15", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit6info1info16", { name: itemname }) }}
              </li>
              <li>{{ $t("policy_tit6info1info17", { name: itemname }) }}</li>
              <li>
                {{ $t("policy_tit6info1info18") }}
              </li>
              <li>{{ $t("policy_tit6info1info19", { name: itemname }) }}</li>
              <li>
                {{ $t("policy_tit6info1info20") }}
              </li>
              <!-- <li>
                {{ $t("policy_tit6info1info21", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit6info1info22") }}
              </li>
              <li>
                {{ $t("policy_tit6info1info23", { name: itemname }) }}
              </li>
              <li>{{ $t("policy_tit6info1info24") }}</li>
              <p>{{ $t("policy_tit6info1info25") }}</p> -->
            </ul>
            <p>
              {{ $t("policy_tit6info2", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit6info3", { name: itemname }) }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("policy_tit7", { name: itemname }) }}</h2>
            <p>
              {{ $t("policy_tit7info1") }}
            </p>
            <p>
              {{ $t("policy_tit7info2") }}
            </p>
          </div>
          <div>
            <h2 class="title">
              {{ $t("policy_tit8", { name: itemname }) }}
            </h2>
            <p>
              {{ $t("policy_tit8info1") }}
            </p>
            <ul>
              <li>{{ $t("policy_tit8info1li1") }}</li>
              <li>
                {{ $t("policy_tit8info1li2") }}
              </li>
              <li>{{ $t("policy_tit8info1li3") }}</li>
              <li>
                {{ $t("policy_tit8info1li4") }}
              </li>
              <li>
                {{ $t("policy_tit8info1li5", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit8info1li6", { name: itemname }) }}
              </li>
              <li>
                {{ $t("policy_tit8info1li7") }}
              </li>
            </ul>
            <p>
              {{ $t("policy_tit8info2") }}
            </p>
            <p>
              {{ $t("policy_tit8info3") }}
            </p>
            <p>
              {{ $t("policy_tit8info4") }}
            </p>
            <p>
              {{ $t("policy_tit8info5", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit8info6", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit8info7", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit8info7_1", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit8info7_2", { name: itemname }) }}
            </p>
            <p>
              {{ $t("policy_tit8info7_3", { name: itemname }) }}
            </p>
            <p>{{ $t("policy_tit8tit9") }}</p>
            <p>
              {{ $t("policy_tit8tit9info1", { name: itemname }) }}
            </p>
            <p>{{ $t("policy_tit8tit10") }}</p>
            <p>
              {{ $t("policy_tit8tit10info1") }}
            </p>
            <p>
              {{ $t("policy_tit8tit10info2", { name: itemname }) }}
            </p>
            <p>{{ $t("policy_tit8tit11") }}</p>
            <p>
              {{ $t("policy_tit8tit11info1") }}
            </p>
            <p>
              {{ $t("policy_tit8tit11info2") }}
            </p>
            <p>
              {{ $t("policy_tit8tit11info3") }}
            </p>
            <p class="">{{ $t("policy_tit8tit12", { name: itemname }) }}</p>
            <p>
              {{ $t("policy_tit8tit12info", { name: itemname }) }}
            </p>
            <p class="">
              {{ $t("policy_tit8tit13") }}
            </p>
            <p>{{ $t("policy_tit8tit13info") }}</p>
            <p>
              {{ $t("policy_tit8tit13info1", { email: email }) }}
            </p>
            <p>
              {{ $t("policy_tit8tit13info2", { name: itemname }) }}
            </p>
            <p>{{ $t("policy_tit8tit13info3") }}</p>
            <p>
              {{ $t("policy_tit8tit13info4", { email: email }) }}
            </p>
            <p>
              {{ $t("policy_tit8tit13info5") }}
            </p>
            <p>
              {{ $t("policy_tit8tit13info6") }}
            </p>
            <p class="">{{ $t("policy_tit8tit14") }}</p>
            <p>
              {{ $t("policy_tit8tit14info", { email: email }) }}
            </p>
            <p>
              {{ $t("policy_tit8tit14info_1", { email: email }) }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <mer-chant-footer></mer-chant-footer>
  </div>
</template>
<script>
import merChantHeader from "./components/mer-chant-header";
import merChantFooter from "./components/mer-chant-footer";
// import { Table, TableColumn } from "element-ui";
export default {
  components: {
    merChantHeader,
    merChantFooter,
    // Table,
  },
  data() {
    return {
      itemname:
        process.env.VUE_APP_ITEM_NAME == "Mbuy"
          ? "Argos"
          : process.env.VUE_APP_ITEM_NAME,
      email: "",
    };
  },
  mounted() {
    this.email = this.$multiItem[process.env.VUE_APP_ITEM_NAME]?.mail;
  },
};
</script>
<style lang="scss" scoped>
.merchantSettled-wap {
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 1200px;
  margin: 0 auto 20px auto;

  .step-div {
    width: 1197px;
    background: #fff;

    border-radius: 4px;
    margin-top: -86px;

    .content {
      padding: 20px 30px;
      border: 1px solid #eeeeee;
      h2 {
        margin-top: 14px;
      }
      .title {
        font-size: 24px;
        color: #0f1111;
        font-weight: 500;
        margin-bottom: 14px;
      }
      .ask {
        color: dodgerblue;
      }
      p,
      ul li {
        font-family: "PingFang HK";
        font-style: normal;
        font-size: 14px;
        line-height: 20px;
        color: #333333;
        padding: 6px 0;
        list-style-type: disclosure-closed;
      }
    }
    .bottom {
      height: 140px;
      font-size: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      align-items: center;
      margin: 20px 0;

      .button {
        width: 475px;
      }
    }
  }
}
@media screen and (max-width: 500px) {
  .merchantSettled {
    width: 100%;
    overflow: hidden;
    .merchantSettled-wap {
      background: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100% !important;
      position: relative;

      .step-div {
        width: 100%;
        background: #fff;

        border-radius: 4px;
        margin-top: -86px;

        .content {
          padding: 20px 30px;
          border: 1px solid #eeeeee;

          .title p {
            font-family: "PingFang HK";
            font-style: normal;
            font-size: 14px;
            line-height: 20px;
            color: #333333;
            padding: 6px 0;
          }
        }

        .bottom {
          height: 100px;
          font-size: 12px;
          display: flex;
          flex-direction: column;
          justify-content: space-around;
          align-items: center;
          margin: 20px 0;

          .button {
            width: 80%;
          }
        }
      }
    }
  }
}
</style>
