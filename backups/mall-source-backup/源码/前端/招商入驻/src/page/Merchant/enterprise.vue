<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('企业证明')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <p>
                {{$t('entTips')}}
            </p>
            <p style="font-weight: 600; margin-bottom:10px">
              1、{{$t('公司照片')}}
            </p>
            <div class="img-box" >
              <img src="@/assets/image/Shop2u/1.jpg" alt="" srcset="">
              <img src="@/assets/image/Shop2u/2.jpg" alt="" srcset="" >
            </div>
            <p style="font-weight: 600;margin-bottom:10px">
              2、{{$t('营业执照')}}
            </p>
            <div class="img-box">
              <img src="@/assets/image/Shop2u/3.jpg" alt="" srcset="">
            </div>
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
import { ImagePreview } from 'vant';
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
  methods: {
    previewImage(url) {
      ImagePreview(url);
    },
  },
};
</script>
<style lang="scss" scoped>

.img-box{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  img{
    width: 48%;
    border-radius: 10px;
  }
}
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
  .img-box{
  display: flex;
  // justify-content: space-between;
  // align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
  img{
    width: 100% !important;
    border-radius: 10px;
    margin-bottom: 10px;
  }
}
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
