<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('about_title')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <div class="title" style="font-size:24px">{{$t('about_title')}}</div>
            <!-- <p>{{ $t("contract_titleInfo", { name: itemname }) }}</p> -->
          </div>
          <div style="margin-top:20px">
            <p >{{$t('about_info1')}}
</p>
            
          </div>
          <div>
            <p >{{$t('about_info2')}}</p>
            
          </div>
          <div  >
            <p>{{$t('about_info3')}}</p>
            <!-- <p>{{ $t("contract_title3info") }}</p>
            <p>{{ $t("contract_title3info1", { name: itemname }) }}</p> -->

          </div>
          <div>
            <p >{{$t('about_info4')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info5')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info6')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info7')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info8')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info9')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info10')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info11')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info12')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info13')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info14')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info15')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info16')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info17')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info18')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info19')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info20')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info21')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info22')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info23')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info24')}}</p>
            
          </div>
          <div>
            <p >{{$t('about_info25')}}</p>
            
          </div>

          <!-- <div>
            <div class="title">{{ $t("contract_title4") }}</div>
            <p>{{ $t("contract_title4info") }}</p>
          </div>
          <div>
            <div class="title">{{ $t("contract_title5") }}</div>
            <p>{{ $t("contract_title5info") }}</p>
            <p>{{ $t("contract_title5info1") }}</p>
          </div>
          <div>
            <div class="title">{{ $t("contract_title6") }}</div>
            <p>{{ $t("contract_title6info") }}</p>
            <p>{{ $t("contract_title6info1") }}</p>
          </div>
          <div>
            <div class="title">{{ $t("contract_title7") }}</div>
            <p>{{ $t("contract_title7info") }}</p>
            <p>{{ $t("contract_title7info1") }}</p>
          </div> -->
          <div style="padding-bottom:50px"></div>
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
      itemname: process.env.VUE_APP_ITEM_NAME=='Mbuy'?'Argos':process.env.VUE_APP_ITEM_NAME,
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
  margin: 0 auto;

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
        margin-top: 14px;
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

        // .content2 {
        //   // padding: 20Px 10Px;
        // }

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
