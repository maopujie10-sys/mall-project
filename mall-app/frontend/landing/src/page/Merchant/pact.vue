<template>
  <div class="merchantSettled" id="merchantSettled">
    <div class="merchantSettled-wap">
      <div class="step-div">
        <!-- step1 -->
        <van-popup
          v-model="show"
          :close-on-click-overlay="false"
          get-container="body"
        >
          <div class="content popup_content">
            <div class="tc_wrap" @scroll="handleScroll">
              <div class="tc" ref="capture" id="originHtml">
                <!-- <p class="title">{{ $t("rzInfo", { name: itemname }) }}</p> -->
                <p class="title">{{ $t("capture_tit") }}</p>
                <!-- <p class="padding-tb">{{ $t("rzTitle1") }}</p> -->
                <p class="padding-tb">
                  {{ $t("capture_info") }}
                </p>
                <p class="padding-tb">{{ $t("capture_info1") }}</p>
                <p class="padding-tb">{{ $t("capture_info2") }}</p>
                <p>
                  <!-- {{ $t("rzTitle1info") }} -->
                  {{ $t("capture_info3") }}
                </p>
                <p>
                  <!-- {{ $t("rzTitle1info1") }} -->
                  {{ $t("capture_info4") }}
                </p>
                <p>{{ $t("capture_info5") }}</p>
                <p>
                  <!-- {{ $t("rzTitle1info2") }} -->
                  {{ $t("capture_info6") }}
                </p>
                <p>
                  {{ $t("capture_info7") }}
                </p>
                <!-- <p class="padding-tb">{{ $t("rzTitle2") }}</p> -->
                <p class="padding-tb">{{ $t("capture_info8") }}</p>
                <p>
                  <!-- {{ $t("rzTitle2info", { name: itemname }) }} -->
                  {{ $t("capture_info9") }}
                </p>
                <p>
                  <!-- {{ $t("rzTitle2info1") }} -->
                  {{ $t("capture_info10") }}
                </p>
                <p>
                  <!-- {{ $t("rzTitle2info2") }} -->
                  {{ $t("capture_info11",{time:itemname=='Argos'?'72':42}) }}
                </p>
                <!-- <p>
              {{ $t("rzTitle2info3") }}
            </p> -->
                <!-- <p class="padding-tb">{{ $t("rzTitle3") }}</p> -->
                <p class="padding-tb">{{ $t("capture_info12") }}</p>
                <p>
                  <!-- {{ $t("rzTitle3info") }} -->
                  {{ $t("capture_info13") }}
                </p>
                <p>
                  <!-- {{ $t("rzTitle3info1") }} -->
                  {{ $t("capture_info14") }}
                </p>
                <p>
                  <!-- {{ $t("rzTitle3info2") }} -->
                  {{ $t("capture_info15") }}
                </p>
                <p>{{ $t("capture_info16") }}</p>
                <!-- <p class="padding-tb">{{ $t("rzTitle4") }}</p> -->
                <!-- <p>
              {{ $t("rzTitle4info") }}
            </p>
            <p>
              {{ $t("rzTitle4info1") }}
            </p> -->
                <div class="esign-content">
                  <div>
                    <p class="padding-tb">
                      {{ $t("capture_info17") }} <span>{{ itemname }}</span>
                     <img src="@/assets/image/seal.png"/>
                    </p>
                    <p class="padding-tb">
                      {{ $t("capture_info19") }}{{ now_date }}
                    </p>
                  </div>

                  <div class="right">
                    <p class="padding-tb">
                      {{ $t("capture_info18")
                      }}<img :src="resultImg" class="esign-img" />
                    </p>
                    <p class="padding-tb">
                      {{ $t("capture_info19") }}{{ now_date }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <van-popup
              v-model="visible"
              class="esign-container"
              :close-on-click-overlay="false"
              get-container="#app"
            >
              <vue-esign
                class="sign-view"
                ref="esign"
                :width="800"
                :height="300"
                :isCrop="isCrop"
                :lineWidth="lineWidth"
                :lineColor="lineColor"
                :bgColor.sync="bgColor"
              />
              <div class="btn-list">
                <div class="btn-left">
                  <van-button type="warning" @click="reset">{{
                    $t("重置")
                  }}</van-button>
                  <van-button type="warning" @click="goback">{{
                    $t("返回上一步")
                  }}</van-button>
                </div>
                <van-button type="primary" @click="save">{{
                  $t("确认")
                }}</van-button>
              </div>
            </van-popup>

            <div class="pop-bnt">
              <van-button
                type="primary"
                class="button"
                :disabled="scrollDisbled"
                @click="agreement"
                >{{ $t("同意并签名") }}</van-button
              >
              <van-button
                type="primary"
                class="button"
                :disabled="tjbtn"
                @click="argeementEsign"
                >{{ $t("确认") }}</van-button
              >
            </div>
          </div>
        </van-popup>
      </div>
    </div>
  </div>
</template>

<script>
import { Toast } from "vant";
import { uploadimg ,upload} from "@/API/commodity";
import vueEsign from "vue-esign";
import html2Canvas from "html2canvas";
import JsPDF from "jspdf";
export default {
  name: "merchantSettled",
  data() {
    return {
      lineWidth: 6,
      lineColor: "#000000",
      bgColor: "",
      resultImg: "",
      // esignImg: "",
      isCrop: false,
      visible: false,
      itemname: '',
      showPassword: true,
      showPassword2: true,
      tjbtn: true,
      isCutting: false, // 是否裁剪
      showUpLoader: true,
      step: 2,
      show: true,
      checked: false,
      screenWidth: document.body.clientWidth,
      signPdfUrl: "",
      token: "",
      pageDiaCode: true,
      renderComponent: true,
      blob: null,
      now_date: "",
    };
  },

  computed: {
    isOverSize() {
      return 4000 * 1024;
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
      for (let v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
          flag = false;
          break;
        }
      }
      return flag;
    },
  },
  components: {
    // cropperjs,
    vueEsign,
    // Uploader,
  },
  created() {
    if (this.screenWidth >= 500) {
      this.labelPosition = "left";
    } else {
      this.labelPosition = "top";
    }
    if (this.$route.query.usercode) {
      localStorage.setItem("usercode", this.$route.query.usercode);
      this.ruleForm.usercode = this.$route.query.usercode;
    }
    if (this.isPC) {
      this.scrollDisbled = false;
    }
    this.getNowFormatDate();
    
  },
  mounted(){
    this.token = sessionStorage.getItem('SellToken')
    this.itemname = sessionStorage.getItem('itemName')
    console.log('this.name ->', this.itemname);
  },
  methods: {
    // 上传签名
   uploadSign(){
       upload({token:this.token,signPdfUrl:(this.signPdfUrl+'')}).then(res=>{
        console.log('res ->', res);
           if(res=="success"){
            Toast(this.$t("成功"));
            setTimeout(()=>{
                window.top.closePopup&&window.top.closePopup()
            },1000)
           } else {
            Toast(this.$t("失败"));
           }
       })
    },
    reset() {
      this.$refs.esign.reset();
    },
    goback() {
      this.$refs.esign.reset();
      this.visible = false;
    },
    getNowFormatDate() {
      let date = new Date(),
        year = date.getFullYear(), //获取完整的年份(4位)
        month = date.getMonth() + 1, //获取当前月份(0-11,0代表1月)
        strDate = date.getDate(); // 获取当前日(1-31)
      if (month < 10) month = `0${month}`; // 如果月份是个位数，在前面补0
      if (strDate < 10) strDate = `0${strDate}`; // 如果日是个位数，在前面补0

      this.now_date = `${year}-${month}-${strDate}`;
    },
    // 保存
    save() {
      // 可选配置参数 ，在未设置format或quality属性时可在生成图片时配置 例如： {format:'image/jpeg', quality: 0.5}
      this.$refs.esign.generate({ format: "image/jpeg", quality: 0.5 });
      this.$refs.esign
        .generate()
        .then((res) => {
          // console.log('res ->', res);
          this.resultImg = res;
          // this.$emit("finsih",res)
          this.visible = false;
          setTimeout(() => {
            this.getImg();
          }, 2000);
        })
        .catch((err) => {
          // 画布没有签字时会执行这里 'Not Signned'
          // this.$message.error("您还未完成签字，请签字完成后保存");
          Toast(this.$t("请签字后再提交"));
        });
    },
    argeementEsign() {
      if (this.signPdfUrl) {
        this.uploadSign();
      } else {
        Toast(this.$t("请签字后再提交"));
      }
    },
    dataURLtoBlob(dataurl) {
      let arr = dataurl.split(","),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new Blob([u8arr], { type: mime });
    },
    blobToFile(theBlob, fileName) {
      theBlob.lastModifiedDate = new Date();
      theBlob.name = fileName;
      return theBlob;
    },
    convertBase64ToFile(urlData, filename) {
      var arr = urlData.split("base64,");
      var type = arr[0].match(/:(.*?);/)[1];
      var fileExt = type.split("/")[1];
      var bstr = atob(arr[1]);
      var n = bstr.length;
      var u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename + "." + fileExt, {
        type: type,
      });
    },
    getImg() {
      this.$refs.capture.scrollTop = 0;
      html2Canvas(this.$refs.capture, {
        allowTaint: true,
        useCORS: true,
      }).then((canvas) => {
        //内容的宽度
        let contentWidth = canvas.width;
        //内容高度
        let contentHeight = canvas.height;
        //一页pdf显示html页面生成的canvas高度,a4纸的尺寸[595.28,841.89];
        let pageHeight = (contentWidth / 592.28) * 841.89;
        //未生成pdf的html页面高度
        let leftHeight = contentHeight;
        //页面偏移
        let position = 0;
        //a4纸的尺寸[595.28,841.89]，html页面生成的canvas在pdf中图片的宽高
        let imgWidth = 595.28;
        let imgHeight = (592.28 / contentWidth) * contentHeight;
        //canvas转图片数据
        let pageData = canvas.toDataURL("image/jpeg", 1.0);
        //新建JsPDF对象
        let PDF = new JsPDF("", "pt", "a4");
        //判断是否分页
        if (leftHeight < pageHeight) {
          PDF.addImage(pageData, "JPEG", 10, 0, imgWidth, imgHeight);
        } else {
          while (leftHeight > 0) {
            PDF.addImage(pageData, "JPEG", 10, position, imgWidth, imgHeight);
            leftHeight -= pageHeight;
            position -= 841.89;
            if (leftHeight > 0) {
              PDF.addPage();
            }
          }
        }
        this.tjbtn = true;
        let blob = this.convertBase64ToFile(
          PDF.output("dataurlstring"),
          "esign.pdf"
        );
        console.log("blob ->", blob);
        let fileOfBlob = new File([blob], "esign.pdf");
        // console.log("fileOfBlob ->", fileOfBlob);
        let formData = new FormData(); //通过formdata上传
        formData.append("file", fileOfBlob);
        formData.append("moduleName", "seller");
        // console.log('formData ->', formData.get("file"));
        Toast.loading({
          duration: 0,
          message: this.$t("上传中"),
          forbidClick: true,
        });
        uploadimg(formData)
          .then((res) => {
            this.signPdfUrl = res;
            this.tjbtn = false;
            Toast(this.$t("签名成功"));
            // this.show = false;
            // this.checked = true;
          })
          .catch(function () {
            Toast.clear();
            Toast(this.$t("失败"));
            this.signPdfUrl = "";
          });
      });
    },
    handleScroll(e) {
      const { scrollTop, clientHeight, scrollHeight } = e.target;
      console.log(scrollTop, clientHeight, scrollHeight);
      if (scrollTop + clientHeight + 2 >= scrollHeight) {
        // alert('滚动到底部啦')
        this.scrollDisbled = false;
      }
    },
    open() {
      // console.log('this.checked ->', this.checked);
      if (this.checked == true) {
        this.checked = false;
      }
      this.checked = false;
      if (this.checked == false) {
        this.show = true;
      }
    },
    agreement() {
      this.visible = true;
      // this.show=false;
      // this.checked=true;
    },
    closeAgreement() {
      this.show = false;
      this.checked = false;
    },

    onOversize(file) {
      console.log(file);
      Toast(this.$t("文件大小不能超过 4Mb"));
    },
    // 裁剪
    handleCutting() {
      this.isCutting = true;
    },
    // 取消
    handleCancel() {
      this.isCutting = false;
      this.fileList1 = [];
    },
    // 上传
    handleUpload(data) {
      let fileOfBlob = new File([data], "logo.png"); // 重命名
      this.isCutting = false;
      Toast.loading({
        duration: 0,
        message: this.$t("上传中"),
        forbidClick: true,
      });
      let formData = new FormData(); //通过formdata上传
      formData.append("file", fileOfBlob);
      formData.append("moduleName", "selle");
      uploadimg(formData)
        .then((data) => {
          Toast.clear();
          this.ruleForm.sellerImg = data;
          console.log("data ->", data);
          this.fileList1[0].content = data;
          // this.fileList1[0].file=fileOfBlob
        })
        .catch(function () {
          Toast.clear();
          Toast(this.$t("失败"));
          this.fileList1 = [];
        });
    },
    updateMerchantInfo(data) {
      this.ruleForm.sellerImg = data;
    },
    handleCropData(data) {
      console.log("裁剪数据");
      console.log(data);
    },
    handleSetLang(index) {
      console.log(index);
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = this.lang[index].key;
      // // 提交mutations
      this.setLanguage(this.lang[index].key);
    },
    changeCountry(val) {
      console.log(val);
      this.ruleForm.country = val;
    },
    //商户注册

    goPage() {
      if (window?.plus) {
        window.open(window.origin + "/www", "_self");
      } else if (this.pc) {
        window.open("https://" + window.location.hostname + "/ww");
      } else {
        window.open("https://" + window.location.hostname + "/ww");
      }
    },

    stepFun() {
      if (!this.checked) {
        Toast(this.$t("请同意入驻协议"));
        return;
      }
      this.step = 2;
      this.$el.querySelector("#product").scrollIntoView({ behavior: "smooth" });
    },
    // openNationality(index) {
    //     const t = this;
    //     if (index === 1) {
    //         this.isCode = true;
    //     } else {
    //         this.isCode = false;
    //     }
    //     this.$refs.controlChild.open();
    //     t.renderComponent = false;
    //     // this.$forceUpdate()
    //     t.$nextTick().then(() => {
    //         t.renderComponent = true;
    //         t.$nextTick().then(() => {
    //             t.sj();
    //         });
    //     });
    // },
    // sj() {
    //     this.$refs.controlChild.open2();
    //     this.$refs.controlChild.open();
    // },
    // getName(params) {
    //     if (this.isCode) {
    //         this.areaCode = params[2];
    //     } else {
    //         this.ruleForm.nationality = params[0];
    //     }
    // },
    //文件上传
    // avatarAfterRead(file) {
    //     this.imgFile = file.content;
    //     this.isCutting = true;
    // },
    //文件上传
    paperworkAfterRead(file, fileIndex) {
      console.log("fileIndex ->", fileIndex);
      const that = this;
      Toast.loading({
        duration: 0,
        message: that.$t("上传中"),
        forbidClick: true,
      });
      let formData = new FormData(); //通过formdata上传
      formData.append("file", file.file);
      formData.append("moduleName", "selle");
      uploadimg(formData)
        .then((data) => {
          Toast.clear();
          that.ruleForm[`idimg_${fileIndex}`] = data;
        })
        .catch(() => {
          Toast.clear();
          Toast(that.$t("失败"));
          that[`fileList${fileIndex + 1}`] = [];
        });
      if (fileIndex == 0) {
        uploadimg(formData)
          .then((data) => {
            Toast.clear();
            Toast(that.$t("成功"));
            that.ruleForm.sellerImg = data;
          })
          .catch(() => {
            Toast.clear();
            Toast(that.$t("失败"));
            that.ruleForm.sellerImg = [];
          });
      }
    },
  },
  beforeDestroy() {
    Toast.clear();
  },
};
</script>
<style lang="scss" scoped>
.rtl{
  .pop-bnt .van-button:nth-child(1){
    margin-right: 0 !important;
    margin-left: 20Px !important;
  }
}
::v-deep {
    .preview-cover {
        position: absolute;
        bottom: 0;
        box-sizing: border-box;
        width: 100%;
        padding: 4px;
        color: #fff;
        font-size: 12px;
        text-align: center;
        background: rgba(0, 0, 0, 0.3);
    }
    .van-button--primary{
        background: #f89220;

        border: 1px solid #f89220;
    }
}
.esign-content{
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    .right{
        margin-right: 200px;
    }
    span{
        position: relative;
        z-index: 999;
    }
    .padding-tb {
    padding:  5px 0 !important;
    display: flex;
    align-items: center;
    position: relative;
    img {
        position: absolute;
        right: -20px;
        top: -20px;
        width: 92px;
        min-height: 92px;
        margin-left: 10px;
    }
    // .esign-img{
    //     position: inherit;
    //     width: 84px;
    //     min-height: 84px;
    //     right: 0;
    //     top: 0;
    // }
}
}
.padding-tb {
    padding: 10px 0 !important;
}

.color-yellow {
    color: var(--color-main) !important;
    cursor: pointer;
    // line-height: 20px;
    display: flex;
    align-items: center;
}

.van-popup {
    width: 1250Px;
    max-height: 90%;
    border-radius: 15px;
}

.popup_content {
    padding: 0 20px;
    max-width: 1250Px;
    .van-button {
        margin: 20px auto 0;
        // width: 100%;
        height: 45px;
        line-height: 45px;
        border-radius: 10px;
        background: var(--color-main);
        color: #fff;
        display: block;
    }

    .close-btn {
        position: absolute;
        top: 20Px;
        right: 20Px;
        width: 24px;
        height: 24px;
        cursor: pointer;

        img {
            width: 100%;
            height: 100%;
        }
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
        width: 1200px;
        margin: 0 auto;
        z-index: 99;

        .step-div {
            width: 100%;
            background: #fff;

            border-radius: 4px;
            margin-top: -46px;

            .content {
                padding: 20px 30px;
                border: 1px solid #eeeeee;

                .title {
                    font-size: 24px;
                    color: #333333;
                    font-weight: 700;
                }

                .info {
                    margin-top: -5px;
                    margin-bottom: 20px;
                    position: relative;
                    z-index: 99;

                    span {
                        color: var(--color-main);
                        cursor: pointer;
                    }
                }

                p {
                    font-family: "PingFang HK";
                    font-style: normal;
                    font-size: 14px;
                    // line-height: 20px;
                    color: #333333;
                    padding: 6px 0;
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
}

/deep/ .van-field__label {
    width: 200px !important;
}

/deep/ .van-tabs__wrap {
    width: 250px;
}

// @media only screen
//     and (device-width: 390px)
//     and (device-height: 844px)
//     and (-webkit-device-pixel-ratio: 3) {
//       .popup_content{
//     padding: 0 0 20px !important;

//   .tc{
//     max-height: 600px;
//     overflow-y: auto;
//     padding: 0 25px;
//     }
//     .close-btn{
//       width: 24px;
//       height: 24px;
//     }
// }
//     }
.tc{
    padding: 20px 10px;
    font-size: 14px;
}
@media (min-width: 768px) and (max-width: 1250px) {
    .van-popup{
        // padding: 0 0 20px !important;
        width: 95% !important;
    }
}
@media screen and (max-width: 768px) {
  .esign-container{
    width: 95% ;
  }
    .esign-content{
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    .right{
        margin-right: 0 !important;
    }
    }
    .pop-bnt{
        width: 100% !important;
        .van-button{
        margin: 0 !important;
        margin-top: 10px !important;
        &:nth-child(1){
        margin-right: 20Px !important;
     }
    }
    }
    .popup_content {
        padding: 0 0 20px !important;
        max-height: 50%;

        .tc_wrap {
            max-height: 500px;
            overflow-y: auto;
            padding: 0 25px;
        }

        // .tc {
        //     max-height: 400px;
        //     overflow-y: auto;
        //     padding: 0 25px;
        // }

        .close-btn {
            width: 24px;
            height: 24px;
            top: 10px;
            right: 10px;
        }
    }

    .merchantSettled {
        width: 100%;

        .merchantSettled-wap {
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100% !important;
            position: relative;
            z-index: 99;

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
                        // line-height: 20px;
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

.demo-ruleForm {
    .uploder-wrap {
        display: flex;
        align-items: center;

        .tips {
            font-size: 12px;
            color: #999999;

            span {
                color: var(--color-main);
            }
        }
    }

    .uploder-center {
        display: flex;

        .uploder-two-wrap {
            margin-right: 30px;

            .tips {
                color: #333333;
                font-size: 12px;
                text-align: center;
                line-height: 1;
            }
        }
    }

    .correct-warp {
        display: flex;

        img {
            width: 100px;
            margin-right: 20px;
        }
    }

    .tab-wrap {
        display: flex;
        margin-top: 20px;
        margin-bottom: 20px;

        .tab-item {
            width: 148px;
            height: 34px;
            background: #eeeeee;
            border-radius: 4px;
            text-align: center;
            cursor: pointer;
            line-height: 34px;
            margin-right: 20px;
            color: #333333;
            font-size: 14px;
        }

        .active {
            color: #fff !important;
            background: var(--color-main) !important;
        }
    }

    .code-input {
        width: 420px;
    }

    .code-wrap {
        width: 133px;
        height: 34px;
        background: var(--color-main);
        border-radius: 4px;
        margin-top: 8px;
        text-align: center;
        line-height: 34px;
        font-size: 14px;
        color: #fff;
        cursor: pointer;
    }

    .el-dropdown {
        width: 100%;
    }

    .prepend-wrap {
        display: flex;
        align-items: center;
        padding: 0 20px;

        .phone_number {
            flex: 1;
        }
    }

    .phone_number_wrap {
        /deep/ .el-input__inner {
            width: 320px;
        }
    }
}

.option-wrap {
    display: flex;
    align-items: center;
    font-size: 14px;

    img {
        height: 30px;
        margin-right: 5px;
    }
}

.lang-item {
    display: flex;
    align-items: center;

    img {
        width: 20px;
        height: 20px;
        margin-right: 5px;
    }
}

/deep/ .van-checkbox__label {
    display: flex;
}

/deep/ .el-form-item__label {
    text-align: left !important;
    line-height: inherit;
}

/deep/ .el-select-dropdown__list {
    padding: 10px 0 !important;
}

/deep/ .el-select .el-input .el-select__caret {
    font-size: 15px;
    display: flex;
    align-items: center;
}

.el-select-dropdown__item.selected {
    color: var(--color-main) !important;
}

.el-select .el-input.is-focus .el-input__inner {
    padding-left: 30px !important;
}

/deep/ .el-input__inner {
    height: 50px !important;
    width: 420px;
    font-size: 14px;
    border: 1px solid #eeeeee;

    &::placeholder {
        font-size: 14px;
        color: #999999;
    }
}

/deep/ .van-uploader__upload-icon {
    font-size: 35px !important;
    color: #aaaaaa !important;
}

/deep/ .el-input-group__prepend {
    width: 100px !important;
    padding: 0 !important;
    background: none !important;
    font-size: 14px;
}

@media screen and (max-width: 768px) {
    .pop-bnt {
        width: 100%;
        margin: 20px auto 0 !important;
        display: flex;
        flex-wrap: wrap;
    }

    /deep/ .el-input__inner {
        width: 100% !important;
    }

    /deep/ .el-select {
        width: 100%;
    }

    .phone_number_wrap {
        /deep/ .el-input__inner {
            width: 100% !important;
        }
    }

    .demo-ruleForm .code-input {
        width: 100%;
    }

    .correct-warp {
        img {
            display: block;
            margin-top: 20px;
            margin-right: 10px !important;
        }
    }
    .van-popup{
        width: 90% !important;
    }
}

/deep/ .van-checkbox__icon--checked .van-icon {
    background-color: var(--color-main) !important;
    border-color: var(--color-main) !important;
}

/deep/ .el-input.is-disabled .el-input__inner {
    background-color: #fff;
}

::-webkit-scrollbar {display: none; /* Chrome Safari */}

.password-icon {
    width: 16px;
    cursor: pointer;
}

.pop-bnt {
    // width: 28%;
    margin: 0 auto 10px;
    display: flex;
    justify-content: center;
    .van-button{
        margin: 0 !important;
        &:nth-child(1){
        margin-right: 20Px !important;
     }

    }
}
.btn-list {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    padding: 10px 0;
    border-top: 1px solid #eee;
    .btn-left {
        display: flex;
        justify-content: center;
    }
    .van-button {
        margin: 5px 10px !important;
    }
}
.esign-container{
    width: 800Px ;
}
</style>
