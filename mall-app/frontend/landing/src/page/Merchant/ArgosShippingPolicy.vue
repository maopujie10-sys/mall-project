<template>
  <div class="merchantSettled">
    <mer-chant-header
      id="product"
      :title="$t('关于卖家计分系统')"
      :shippingInfo="$t('（罚分/扣分规则）')"
    ></mer-chant-header>
    <div class="merchantSettled-wap">
      <div class="step-div">
        <div class="content">
          <div>
            <p>
              {{ $t("简介：让您了解卖家信用分系统是什么，店铺计分如何产生，计分，恢复等") }}
            </p>
            <p>{{ $t("Ashopping-info1-0")}}<span class="shopLink" @click="goShop">ArgosShop</span></p>
            <p>{{ $t("Ashopping-info1") }}</p>
          </div>
          <div class="">
            <h2 class="title">{{ $t("一、如何进入卖家计分系统？") }}</h2>
            <p>
              {{ $t("Ashopping-title1info") }}
            </p>
            <p>{{ $t("如果未达成表现目标，则会导致信用分降低。") }}</p>
            <p>
              {{ $t("您可以在【卖家中心>>卖家信用分】页面下查看我的信用分，包括目前的信用分。") }}
              <br>{{$t("Ashopping-title1info-3")}}
            </p>
            <!-- <p>{{ $t("Ashopping-title1info-3") }}</p> -->
          </div>
          <div>
            <h2 class="title">{{ $t("二、信用分是如何产生的？") }}</h2>
            <div>
              <p>
                {{ $t("若未达到买家的最低预期，则可能产生信用分扣除。同时将会收到来自平台的通知。") }}
              </p>
              <p>
                {{ $t("卖家计分系统会根据卖家未达目标的违规项目更新计分。您可以点击对应信用分维度关键词查看完整政策。") }}
              </p>
              <el-table
                :data="tableData"
                :span-method="objectSpanMethod"
                border
                style="width: 100%; margin-top: 20px"
              >
                <el-table-column
                  prop="id"
                  :label="$t('信用分维度')"
                  width="240"
                >
                </el-table-column>
                <el-table-column
                  width="410"
                  prop="name"
                  :label="$t('Ashopping-table1-header-1')"
                >
                </el-table-column>
                <el-table-column
                  width="200"
                  prop="amount1"
                  :label="$t('每月给予计分')"
                >
                </el-table-column>
              </el-table>
            </div>
            <div>
              <h2 class="title" style="font-size:20px">{{ $t("Ashopping-title4") }}</h2>
              <p class="title" style="font-size:15px;margin-bottom:0">{{ $t("Ashopping-title4-qs1") }}</p>
              <p>
                {{ $t("Ashopping-title4-d") }}
              </p>
              <p class="title" style="font-size:15px;margin-bottom:0">{{ $t("Ashopping-title4-qs2") }}</p>
              <p>{{ $t("Ashopping-title4-d1") }}</p>
              <p>
                {{ $t("Ashopping-title4-d2") }}
              </p>
            </div>

            <div>
              <h2 class="title" style="font-size:20px">{{ $t("违背承诺的规则及实施细则") }}</h2>
              <p class="title" style="font-size:20px;margin-bottom:0">{{ $t("Ashopping-title5-qs") }}</p>
              <p class="title" style="font-size:15px;margin-bottom:0;line-height: normal;">
                {{ $t("【适用情形】违背承诺，是指商家未按照承诺向买家提供服务，侵害买家权益或未按照承诺向买家履行义务的行为。商家须继续履行法定或约定的如实描述、换货、退货、退款。") }}
              </p>
            </div>

            <div>
              <h2 class="title" style="font-size:20px">{{ $t("【处理措施】扣除信用分（一般违规）") }}</h2>
              <p class="title" style="font-size:15px;margin-bottom:0">{{ $t("【具体处理措施】") }}</p>
              <p class="title" style="font-size:15px;margin-bottom:0">
                {{ $t("（一）商家就已付款订单或特殊情形下对应的商品或服务有未履行的其它承诺的，每次扣一般违规行为5分。") }}
              </p>
              <p class="title" style="font-size:15px;margin-bottom:0">
                {{ $t("（二）商家违背以下任一承诺的，每次扣情节严重的行为10分：") }}
              </p>
              <p>
                {{$t("Ashopping-title5-d1-tit-2-1")}}
              </p>
              <p>
                {{$t("Ashopping-title5-d1-tit-2-2")}}
              </p>
              <p>
                {{$t("3、未经买卖双方协商拒绝向买家发送或延迟发送已承诺提供的试用商品的；")}}
              </p>
              <p>
                {{$t("4、商家就已付款订单72小时未处理订单的；")}}
              </p>
              <p>
                {{$t("5、商家未经协商及通知买家，下架已销售，未送达的产品，导致买家无法及时查看；")}}
              </p>
               <p class="title" style="font-size:15px;margin-bottom:0">
                {{ $t("（三）情节特别严重的") }}
              </p>
              <p>
                {{$t("1、加入Argosshop官方活动的商家，未按照活动要求（除发货时间外）履行的；")}}
              </p>
              <p>
                {{$t("Argosshop官方发布的其他管理内容（包括但不限于规则、规范、类目管理标准、行业标准等），对上述行为的规定符合特定情形的，从其规定。")}}
              </p>
              <p>
                {{$t("除上述列举的行为外，Argosshop官方发布的其他管理内容（包括但不限于规则、规范、类目管理标准、行业标准等）中认为构成违背承诺行为的，从其规定。")}}
              </p>
            </div>

            <div>
<!--              <h2 class="title">-->
<!--                {{ $t("三、计分对应的处分是什么？") }}-->
<!--              </h2>-->
<!--             <p class="title" style="font-size:15px;margin-bottom:0">-->
<!--                {{ $t("如果卖家累积了大量计分，将根据下表暂停卖家的部分销售权益：") }}-->
<!--              </p>-->
              <el-table
                :data="tableData2"
                border
                style="width: 100%; margin-top: 20px"
              >
                <el-table-column
                  prop="name"
                  :label="$t('累计计分')"
                  width="180"
                >
                </el-table-column>
                <el-table-column prop="lev1" label="10" align="center">
                </el-table-column>
                <el-table-column prop="lev2" label="20" align="center">
                </el-table-column>
                <el-table-column prop="lev3" label="25" align="center">
                </el-table-column>
                <el-table-column prop="lev4" label="30" align="center">
                </el-table-column>
                <el-table-column prop="lev5" label="35" align="center">
                </el-table-column>
                <el-table-column prop="lev6" label=">40" align="center">
                </el-table-column>
              </el-table>
            </div>



            <div>
              <h2 class="title">{{ $t("四、处分会持续多长时间？") }}</h2>
              <p v-if="itemname !== 'GreenMall'">
                {{ $t("处罚将会永久有效，但只要采取相应措施，改善目前的店铺表现并保持至达标，受处分的卖家将重新获得某些销售权益，请在28天内恢复您的信用分。") }}
              </p>
              <p v-else>
                {{$t("Ashopping-title6info1")}}
              </p>
            </div>

            <div>
              <h2 class="title">{{ $t("Ashopping-title7") }}</h2>
              <p>
                {{ $t("（一）情节一般的：消费者发起投诉且经Argosshop判定投诉成立的。每次扣一般违规5分。完成5个订单即可恢复5分。（若在店铺积分恢复中时，再次发生类似投诉，订单积分恢复将清零）") }}
              </p>
              <p>
                {{ $t("（二）情节严重的：消费者发起投诉且经Argosshop判定投诉成立的，每次扣一般违规20分。完成20个订单即可恢复20分。（若在店铺积分恢复中时，再次发生类似投诉，订单积分恢复将清零。若连续违规将给予冻结店铺并清退店铺）") }}
              </p>
              <p>{{ $t("（三）情节特别严重的：给予永久封禁店铺清退店铺的处理。") }}</p>
              <p>{{ $t("（四）特例：Argos直营店，均受Argos直属部门管理，如出现情节特别严重的违规行为，将会取消Argos直营店资格，并处于永久封禁店铺，清退店铺等处罚，并处于店铺获利的30%作为罚款。") }}</p>
              <p>
                <span>{{ $t("例1：卖家A在第3周产生3个计分，在第7周会重新获得权益") }}</span>
              </p>
              <img
                src="@/assets/image/argos1.png"
                alt=""
              />

              <p>
                <span>{{ $t("例2：卖家B在第3周产生3个计分，在第5周产生3个计分，两次计分会累积计算等级，在第9周会重新获得权益") }}</span>
              </p>
              <img
                src="@/assets/image/argos2.png"
                alt=""
              />

              <p>
                <span>{{ $t("例3：卖家C在新季度开始前1周产生3个计分，新季度开始后又产生3个计分，新产生的计分会重新计算等级") }}</span>
              </p>
              <img
                src="@/assets/image/argos3.png"
                alt=""
              />

            </div>
            <div>
              <h2 class="title">{{ $t("六、卖家等级信用分条款") }}</h2>
              <p>
                {{ $t("bottom1",{ a: "C" , b:"1",c:"1"}) }}
              </p>
              <p>
                {{ $t("bottom1",{ a: "B" , b:"3",c:"2"}) }}
              </p>
              <p>
                {{ $t("bottom1",{ a: "A" , b:"5",c:"3"}) }}
              </p>
              <p>
                {{ $t("bottom1",{ a: "S" , b:"8",c:"4"}) }}
              </p>
              <p>
                {{ $t("bottom1",{ a: "SS" , b:"10",c:"5"}) }}
              </p>
              <p>
                {{ $t("bottom1",{ a: "SSS" , b:"15",c:"6"}) }}
              </p>
            </div>
            <div>
              <h2 class="title">{{ $t("Ashopping-title8") }}</h2>
              <p>
               {{ $t("联系在线人工客服申诉。如果您申诉成功，我们将取消您的计分并恢复您相应的销售权益。") }}
              </p>
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
import { mapGetters } from "vuex";
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
      // tableData: [
      //   {
      //     id: this.$t("Ashopping-table1-row"),
      //     name: this.$t("Ashopping-table1-row1-clo1"),
      //     amount1: this.$t("Ashopping-table1-row1-clo3"),
      //   },
      //   {
      //    id: this.$t("Ashopping-table1-row1"),
      //     name: this.$t("Ashopping-table1-row1-clo2",{time:process.env.VUE_APP_ITEM_NAME == "Inchoi" || process.env.VUE_APP_ITEM_NAME == "GreenMall"?'48':'72'}),
      //     // amount1: this.$t("Ashopping-table1-row1-clo3"),
      //   },
      //   {
      //     id: this.$t("Ashopping-table1-row2"),
      //     name: this.$t("Ashopping-table1-row2-clo1"),
      //     amount1: this.$t("Ashopping-table1-row2-clo4"),
      //   },
      //   {
      //     // id: "客户服务",
      //     name: this.$t("Ashopping-table1-row2-clo2"),
      //     amount1: this.$t("Ashopping-table1-row1-clo3"),
      //   },
      //   {
      //     id: this.$t("Ashopping-table1-row3"),
      //     name: this.$t("Ashopping-table1-row2-clo3"),
      //     amount1: this.$t("Ashopping-table1-row1-clo3"),
      //   },
      //   {
      //     // id: "违背承诺",
      //     name: this.$t("Ashopping-table1-row3-clo1"),
      //     amount1: this.$t("Ashopping-table1-row1-clo3"),
      //   },
      // ],
      // tableData2: [
      //   {
      //     name: this.$t("Ashopping-table2-header2"),
      //     lev1: this.$t("Ashopping-table2-j")+ "1" ,
      //     lev2: this.$t("Ashopping-table2-j")+ "2" ,
      //     lev3: this.$t("Ashopping-table2-j")+ "3",
      //     lev4: this.$t("Ashopping-table2-j")+ "4",
      //     lev5: this.$t("Ashopping-table2-j")+ "5",
      //     lev6: this.$t("Ashopping-table2-j")+ "6",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row", { name: this.itemname }),
      //     lev1: "●",
      //     lev2: "●",
      //     lev3: "●",
      //     lev4: "●",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row1", { name: this.itemname }),
      //     lev1: "",
      //     lev2: "●",
      //     lev3: "●",
      //     lev4: "●",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row2"),
      //     lev1: "",
      //     lev2: "●",
      //     lev3: "●",
      //     lev4: "●",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row3"),
      //     lev1: "",
      //     lev2: "",
      //     lev3: "●",
      //     lev4: "●",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row4"),
      //     lev1: "",
      //     lev2: "",
      //     lev3: "",
      //     lev4: "●",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      //   {
      //     name: this.$t("Ashopping-table2-row5"),
      //     lev1: "",
      //     lev2: "",
      //     lev3: "",
      //     lev4: "",
      //     lev5: "●",
      //     lev6: "●",
      //   },
      // ],
      lang: [
        {
          title: "简体中文",
          key: "zh-CN",
          icon: require("@/assets/image/language/cn.png"),
        },
        {
          title: "English",
          key: "en-US",
          icon: require("@/assets/image/language/usa.png"),
        },
        {
          title: "繁体中文",
          key: "CN",
          icon: require("@/assets/image/language/tw.png"),
        },
      ],
    };
  },
  computed: {
    tableData2(){
      return [
        {
          name: this.$t("Ashopping-table2-header2"),
          lev1: this.$t("Ashopping-table2-j")+ "1" ,
          lev2: this.$t("Ashopping-table2-j")+ "2" ,
          lev3: this.$t("Ashopping-table2-j")+ "3",
          lev4: this.$t("Ashopping-table2-j")+ "4",
          lev5: this.$t("Ashopping-table2-j")+ "5",
          lev6: this.$t("Ashopping-table2-j")+ "6",
        },
        {
          name: this.$t("Ashopping-table2-row", { name: this.itemname }),
          lev1: "●",
          lev2: "●",
          lev3: "●",
          lev4: "●",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("Ashopping-table2-row1", { name: this.itemname }),
          lev1: "",
          lev2: "●",
          lev3: "●",
          lev4: "●",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("不允许上架/修改商品（更改库存除外）（28天）"),
          lev1: "",
          lev2: "",
          lev3: "●",
          lev4: "●",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("Ashopping-table2-row3"),
          lev1: "",
          lev2: "●",
          lev3: "●",
          lev4: "●",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("商品将不会出现在浏览页面中（28天）"),
          lev1: "",
          lev2: "",
          lev3: "",
          lev4: "",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("Ashopping-table2-row5"),
          lev1: "",
          lev2: "",
          lev3: "",
          lev4: "",
          lev5: "●",
          lev6: "●",
        },
        {
          name: this.$t("限制卖家部分店铺功能（提款，下架，注销）"),
          lev1: "●",
          lev2: "●",
          lev3: "●",
          lev4: "●",
          lev5: "●",
          lev6: "●",
        },
      ]
    },
    tableData(){
      return  [
        {
          id: this.$t("Ashopping-table1-row"),
          name: this.$t("卖家在7天内取消或更改数量的订单占总订单数量的2%"),
          amount1: this.$t("最高20分"),
        },
        {
         id: this.$t("Ashopping-table1-row1"),
          name: this.$t("卖家在7天内超过72小时延迟发货的订单数量占总订单数量的3%"),
          // amount1: this.$t("Ashopping-table1-row1-clo3"),
        },
        {
          id: this.$t("Ashopping-table1-row2"),
          name: this.$t("Ashopping-table1-row2-clo1"),
          amount1: this.$t("最高20分"),
        },
        {
          // id: "客户服务",
          name: this.$t("卖家主动要求买家取消订单数量超过3次"),
          amount1: this.$t("最高10分"),
        },
        {
          id: this.$t("Ashopping-table1-row3"),
          name: this.$t("回应买家率低于85%"),
          amount1: this.$t("最高10分"),
        },
        {
          // id: "违背承诺",
          name: this.$t("Ashopping-table1-row3-clo1"),
          amount1: this.$t("最高20分"),
        },
        {
          // id: this.$t("Ashopping-table1-row4"),
          id: this.$t('恶意刷单'),
          name:this.$t('商家雇佣或者使用本平台买家账户对本人账户下单以及多次下单'),
          amount1: this.$t("罚款 关店"),
        }
      ]
    },
    isPC() {
      let userAgentInfo = navigator.userAgent;
      let Agents = [
        "Android",
        "iPhone",
        "SymbianOS",
        "Windows Phone",
        "iPad",
        "iPod",
      ];
      let flag = true;
      for (var v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
          flag = false;
          break;
        }
      }
      return flag;
    },
    languageIcon() {
      const language = this.$store.getters.language || "CN";
      const icon = {
        "zh-CN": require("@/assets/image/language/cn.png"),
        "en-US": require("@/assets/image/language/usa.png"),
        CN: require("@/assets/image/language/tw.png"),
      };
      return icon[language];
    },
    ...mapGetters({
      activeLang: "language",
    }),
  },
  methods: {
    goShop(){
      window.open('https://argos.me/#/index','_black')
    },
    goLink(){
      window.open('https://t.me/Argos002','_black')
    },
    objectSpanMethod({ rowIndex, columnIndex }) {
      console.log("columnIndex ->", columnIndex);
      if (columnIndex === 0 ) {
        console.log('rowIndex ->', rowIndex);
        if(rowIndex === 0 || rowIndex  === 1){
          return {
            rowspan: 1,
            colspan: 1,
          }
          } else if (rowIndex % 2 === 0 && rowIndex  !== 1) {
          return {
            rowspan: 2,
            colspan: 1,
          };
        } else {
          return {
            rowspan: 0,
            colspan: 0,
          };
        }
      }
      if(columnIndex === 2){
        if(rowIndex === 0 || rowIndex  === 1){
          return {
            rowspan: 2,
            colspan: 1,
          }}else{
          return {
            rowspan: 1,
            colspan: 1,
          };
        }
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.shopLink{
  color: blue;
  position: relative;
  z-index: 9;
  cursor: pointer;
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
        font-size: 14px;
        line-height: 20px;
        color: #333333;
        padding: 6px 0;
        list-style-type: disc;
      }
    }
    img {
      max-width: 100%;
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
