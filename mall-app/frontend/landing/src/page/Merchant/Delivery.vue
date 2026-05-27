<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('delivery_title')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <div class="title">{{ $t("delivery_q1") }}</div>
            <p>
              {{ $t("delivery_d1",{num: itemname !== 'INT Overstock'?'112':'180'}) }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("delivery_q2") }}</h2>
            <p v-if="itemname !== 'INT Overstock'">
              {{ $t("delivery_d2", { name: itemname }) }}
            </p>
            <p v-else>
              {{ $t("delivery_d2_Int") }}
            </p>
            <p>
              {{ $t("delivery_d2_1") }}
            </p>
            <p v-if="itemname !== 'INT Overstock'">
              {{ $t("delivery_d2_2") }}
            </p>
            <p v-else>
              {{ $t("delivery_d2_2_int") }}
            </p>
            <p>
              {{ $t("delivery_d2_3") }}
            </p>
          </div>
          <div>
            <h2 class="title">{{ $t("delivery_tit") }}</h2>
            <p class="" style="font-weight: 600">{{ $t("delivery_q3") }}</p>
            <p>
              {{ $t("delivery_d3") }}
            </p>
            <p class="" style="font-weight: 600">{{ $t("delivery_q4") }}</p>
            <p>
              {{ $t("delivery_d4") }}
            </p>
            <p class="" style="font-weight: 600">{{ $t("delivery_q5") }}</p>
            <p>
              {{ $t("delivery_d5") }}
            </p>
            <p class="" style="font-weight: 600">{{ $t("delivery_q6") }}</p>
            <p>
              {{ $t("delivery_d6") }}
            </p>
            <p>
              {{ $t("delivery_d7") }}
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
        font-size: 14px;
        line-height: 20px;
        color: #333333;
        padding: 6px 0;
        list-style-type: disc;
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
