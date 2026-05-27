<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('returnPolicy_title')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <div class="title">{{ $t("returnPolicy_tit1") }}</div>
            <p>
              {{ $t("returnPolicy_tit1info") }}
            </p>
            <p>{{ $t("returnPolicy_tit1info1") }}</p>
            <ul>
              <li>{{ $t("returnPolicy_tit1li1") }}</li>
              <li>{{ $t("returnPolicy_tit1li2") }}</li>
              <li>{{ $t("returnPolicy_tit1li3") }}</li>
              <li>{{ $t("returnPolicy_tit1li4") }}</li>
              <li>{{ $t("returnPolicy_tit1info2") }}</li>
            </ul>
            <p>
              {{ $t("returnPolicy_tit1info3") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("returnPolicy_tit2") }}</h2>
            <p>
              {{ $t("returnPolicy_tit2info") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("returnPolicy_tit3") }}</h2>
            <p>
              {{ $t("returnPolicy_tit3info") }}
            </p>
            <p>
              {{ $t("returnPolicy_tit3info1",{num: itemname !== 'INT Overstock'?'112':'180'}) }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("returnPolicy_tit4") }}</h2>
            <p>
              {{ $t("returnPolicy_tit4info") }}
            </p>
            <ul>
              <li>
                {{ $t("returnPolicy_tit4li1") }}
              </li>
              <li>
                {{ $t("returnPolicy_tit4li2") }}
              </li>
              <li>
                {{ $t("returnPolicy_tit4li3") }}
              </li>
              <li>{{ $t("returnPolicy_tit4li4") }}</li>
            </ul>
            <p>
              {{ $t("returnPolicy_titinfo1") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("returnPolicy_tit5") }}</h2>
            <p>{{ $t("returnPolicy_tit5q1") }}</p>
            <p>
              {{ $t("returnPolicy_tit5d1", { name: itemname }) }}
            </p>
            <p>
              {{ $t("returnPolicy_tit5d1p") }}
            </p>
            <p>
              {{ $t("returnPolicy_tit5d1p1") }}
            </p>
            <p class="title">{{ $t("returnPolicy_titq2") }}</p>
            <p>{{ $t("returnPolicy_titq2p", { name: itemname }) }}</p>
            <ul>
              <li>{{ $t("returnPolicy_titd2li1") }}</li>
              <li>{{ $t("returnPolicy_titd2li2") }}</li>
              <li>{{ $t("returnPolicy_titd2li3") }}</li>
              <li>{{ $t("returnPolicy_titd2li4") }}</li>
            </ul>
            <p>
              {{ $t("returnPolicy_titd2info") }}
            </p>
            <ul>
              <li>{{ $t("returnPolicy_titd2li5") }}</li>
              <li>{{ $t("returnPolicy_titd2li6") }}</li>
            </ul>
            <p class="title">{{ $t("returnPolicy_titq3") }}</p>
            <p>{{ $t("returnPolicy_titd3", { name: itemname }) }}</p>
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
    };
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
        list-style: none;
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
