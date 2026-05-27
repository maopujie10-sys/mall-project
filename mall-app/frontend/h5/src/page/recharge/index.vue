<template>
    <div class="recharge" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed :title="itemName == 'Hive' ? $t('加值') : $t('充值')" left-arrow
            @click-left="onClickLeft" :right-text="$t('记录')" @click-right="onClick1" />
        <div style="width: 100%;" class="h46"></div>
        <div class="biaoti">{{ $t('区块链网络') }}</div>
        <div class="duoxuan">
            <!--      <div class="xuan1 weixuan">111</div>-->
            <!--      {{tongdao_xuanzhong}}-->
            <div v-for="(item, indx) in tongdao" :key="indx" class="xuan1"
                :class="tongdao_xuanzhong.blockchain_name === item.blockchain_name ? 'xuanzhong' : 'weixuan'"
                @click="tongdao_qiehuan(item)">{{ item.blockchain_name }}
                <!-- <img class="xuanzhong-img" v-if="tongdao_xuanzhong.blockchain_name === item.blockchain_name"
                    src="@/assets/image/public/block_choose.png" /> -->
                <van-icon v-if="tongdao_xuanzhong.blockchain_name === item.blockchain_name" class-prefix="icon"
                    name="xuanzejiaobiao" class="xuanzhong-img rtl_selected" />
            </div>
        </div>
        <div class="qrcode" style="display: flex;justify-content: center;margin-top: 20px;width: 100%;float: left;">
            <canvas id="canvas" style="display:none"></canvas>
            <img :src="imgUrl" style="width: 150px;height: 150px;" />
        </div>
        <div class="baocunerweima">
            <div class="baocunerweima-buuon" @click="baocunhaibao">{{ $t('保存二维码') }}</div>
        </div>
        <div class="biaoti">{{ $t('充值地址') }}</div>
        <div class="chongzhifuzhi">
            <div class="chongzhifuzhi2">
                <div class="dizhi">{{ tongdao_xuanzhong.address }}</div>
                <div style="flex: 1;"></div>
                <div class="fuzhi11" style="color: var(--main-color);" @click="copyData(tongdao_xuanzhong.address)">{{
                    $t('复制') }}
                </div>
            </div>
        </div>
        <div class="biaoti" style="margin-bottom: 5px;">{{ $t('充值数量') }}</div>
        <div class="shuru">
            <el-input :placeholder="$t('请输入充值数量')" type="number" v-model="it.input1" clearable @input="handleInput">
            </el-input>
        </div>
        <div class="biaoti">{{ $t('预计到账') }}({{ $t('当前汇率') }} 1 : {{ tongdao_xuanzhong.fee > 1 ?
            priceFormat(tongdao_xuanzhong.fee) : tongdao_xuanzhong.fee }})</div>
        <div class="chongzhifuzhi">
            <div class="chongzhifuzhi2">
                <div class="dizhi">{{ priceFormat(it.input1 * tongdao_xuanzhong.fee) }}</div>
                <div style="flex: 1;"></div>
                <div class="fuzhi11" style="">USDT</div>
            </div>
        </div>
        <div class="biaoti" style="margin-bottom: 10px; ">{{ $t('上传图片（上传支付详情截图）') }}</div>
        <div class="shangchaun" style="margin-left: 15px;width:100%;float: left;">
            <van-uploader v-model="fileList" multiple :max-count="1" preview-size="120px" :after-read="afterRead"
                accept=".png,.jpg,.jpeg" />
        </div>
        <div class="tijiao">
            <div class="tijiao2" @click="biaodan_tijiao">{{ $t('提交') }}</div>
        </div>
    </div>
</template>
<script>
import QRCode from 'qrcode'
import { Toast, Uploader, Icon } from 'vant';
import { priceFormat } from '@/utils/utis'
import { chongzhitijiao_post, session_token, tupianshangchuan_post, zhifutongdao_post } from "@/API/user";
export default {
    data() {
        return {
            priceFormat,
            itemName: process.env.VUE_APP_ITEM_NAME,
            data: {},
            codes: '',
            tongdao_xuanzhong: {},
            imgUrl: null,
            tongdao: [],
            it: {
                input1: '',
            },
            fileList: [],
            shangchuanurl: '',
            session_token: ''
        }
    },
    components: {
        QRCode: QRCode,
        [Icon.name]: Icon,
        [Uploader.name]: Uploader
    },
    created() {
        // this.$nextTick(function () {
        //   this.useqrcode1()
        // })
        // this.useqrcode1()\
        this.zhifutongdao()

    },
    methods: {
        handleInput() {
            this.it.input1 = this.it.input1.replace(/[^\d.]/g, ""); // 非数字和小数点替换为空字符串
            this.it.input1 = this.it.input1.replace(/\.{2,}/g, "."); // 连续出现多个小数点替换为单个小数点
            this.it.input1 = this.it.input1.replace(/^\./g, ""); // 第一个字符如果是小数点则替换为空字符串
            this.it.input1 = this.it.input1.replace(".", "$#$").replace(/\./g, "").replace("$#$", "."); // 将第一个小数点替换为$#$，去除所有小数点，再将$#$替换回小数点
            if (['BTC', 'ETH'].includes(this.$route.query.type)) {
                this.it.input1 = this.it.input1.replace(/^(\-)*(\d+)\.(\d{0,10}).*$/, "$1$2.$3"); // 最多允许输入10位小数
                this.it.input1 = this.it.input1.replace(/^\D*(\d{0,10}(?:\.\d{0,10})?).*$/g, "$1"); // 最多允许输入10位数字
            } else {
                this.it.input1 = this.it.input1.replace(/^(\-)*(\d+)\.(\d{0,2}).*$/, "$1$2.$3"); // 最多允许输入2位小数
                // this.it.input1 = this.it.input1.replace(/^\D*(\d{0,2}(?:\.\d{0,10})?).*$/g, "$1"); // 最多允许输入10位数字
            }

        },
        biaodan_tijiao() {
            var t = this
            if (this.it.input1 === '') {
                Toast(t.$t('请输入充值数量'));
                return
            }
            if (this.shangchuanurl === '') {
                Toast(t.$t('请上传图片'));
                return
            }
            if ((this.it.input1 * this.tongdao_xuanzhong.fee).toFixed(2) < this.tongdao_xuanzhong.recharge_limit_min) {
                Toast(t.$t('充值价值不得小于最小限额') + this.tongdao_xuanzhong.recharge_limit_min + 'usdt')
                return
            }
            if ((this.it.input1 * this.tongdao_xuanzhong.fee).toFixed(2) > this.tongdao_xuanzhong.recharge_limit_max) {
                Toast(t.$t('充值价值不得大于最大限额') + this.tongdao_xuanzhong.recharge_limit_max + 'usdt')
                return
            }
            session_token({}).then(res => {
                this.session_token = res.session_token
                this.chongzhitijiao()
            })
        },
        chongzhitijiao() {
            var data = {
                'session_token': this.session_token,
                'amount': this.it.input1,
                'from': '123',
                'blockchain_name': this.tongdao_xuanzhong.blockchain_name,
                'img': this.shangchuanurl,
                'coin': this.tongdao_xuanzhong.coin,
                'channel_address': this.tongdao_xuanzhong.address,
                'tx': '123',
            };
            Toast.loading({
                duration: 0,
                forbidClick: true,
                loadingType: "spinner",
                message: ""
            });
            chongzhitijiao_post(data).then(res => {

                Toast.clear();
                Toast(this.$t('提交成功'));
                this.it.input1 = ''
                this.fileList = []
                this.shangchuanurl = ''
                this.$router.push('/SubmitCompleted?path=rechargeRecord')


            }).catch(err => {
                // Toast.clear()
                // reject(err)
                Toast.clear();
                // Toast(this.$t(err.msg));
            }
            )
        },
        tongdao_qiehuan(e) {
            this.tongdao_xuanzhong = e
            this.useqrcode1()
        },
        zhifutongdao() {
            zhifutongdao_post({}).then(res22 => {
                // this.code = this.$route.query.usercode

                for (var i = 0; i < res22.length; i++) {
                    if (res22[i]['coin'] === this.$route.query.type) {
                        this.tongdao.push(res22[i])
                    }
                }
                this.tongdao_xuanzhong = this.tongdao[0]
                this.useqrcode1()
            })
        },
        afterRead(file) {
            Toast.loading({
                duration: 0,
                forbidClick: true,
                loadingType: "spinner",
                message: ""
            });
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file);
            formData.append('moduleName', "recharge")
            tupianshangchuan_post(formData).then(res => {
                Toast.clear();
                this.shangchuanurl = res
            }).catch(function (err) {
                Toast.clear();
                Toast(this.$t('添加失败'));
                this.fileList = []
            })
        },
        copyData(ea) {
            //如果需要回调：
            this.$copyText(ea).then(e => {
                Toast(this.$t('复制成功'))
            }, function (e) {
                Toast(this.$t('复制失败'))
            })
        },
        copyData2(ea) {
            //如果需要回调：
            this.$copyText(ea).then(e => {
                // alert('复制成功')
            }, function (e) {
                // alert('复制失败')
            })
        },
        useqrcode1() {//生成二维码
            let canvas = document.getElementById('canvas')
            let url = this.tongdao_xuanzhong.address
            QRCode.toCanvas(canvas, url, function (error) {
                if (error) {
                } else {
                }
            })
            this.saveImg()//保存图片
        },
        baocunhaibao() {
            let myCanvas = document.getElementsByTagName('canvas');
            this.imgUrl = myCanvas[0].toDataURL('image/png')
            this.getUrlBase64(this.imgUrl).then(base64 => {
                let link = document.createElement('a')
                link.href = base64
                link.download = 'qrCode.png'
                link.click()
            })
        },
        getUrlBase64(url) {
            return new Promise(resolve => {
                let canvas = document.createElement('canvas')
                let ctx = canvas.getContext('2d')
                let img = new Image()
                img.crossOrigin = 'Anonymous' //允许跨域
                img.src = url
                img.onload = function () {
                    canvas.height = 300
                    canvas.width = 300
                    ctx.drawImage(img, 0, 0, 300, 300)
                    let dataURL = canvas.toDataURL('image/png')
                    canvas = null
                    resolve(dataURL)
                }
            })
        },
        //保存图片
        saveImg() {
            let myCanvas = document.getElementsByTagName('canvas');
            this.imgUrl = myCanvas[0].toDataURL('image/png')
        },
        onClickLeft() {
            this.$router.push({ path: '/rechargeList', dir: 'left' })
        },
        onClick1() {
            this.$router.push({ path: '/rechargeRecord' })
        }
    },

}
</script>
<style lang="scss" scoped>
.recharge {
    width: 100%;
    height: 100%;

    .biaoti {
        float: left;
        margin-top: 20px;
        width: 90%;
        margin-bottom: 10px;
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        color: #333333;
        margin-left: 15px;
    }

    .duoxuan {
        width: 100%;

        .xuan1 {
            float: left;
            margin-left: 15px;
            width: 100px;
            height: 40px;
            text-align: center;
            position: relative;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 40px;
            border-radius: 4px;
        }

        .weixuan {
            color: #999999;
            border: 1px solid #999999;
        }

        .xuanzhong {

            color: var(--main-color);
            border: 1px solid var(--main-color);
        }

        .xuanzhong-img {
            font-size: 40px;
            position: absolute;
            right: -1px;
            bottom: 0;
        }
    }

    .baocunerweima {
        display: flex;
        justify-content: center;
        //margin-top: 30px;
        width: 100%;
        float: left;

        .baocunerweima-buuon {
            width: 114px;
            height: 40px;
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 40px; //
            text-align: center;

            /* 333 */

            color: #333333;
        }
    }

    .chongzhifuzhi {
        float: left;
        padding-left: 15px;
        padding-right: 15px;
        box-sizing: border-box;
        width: 100%;

        .chongzhifuzhi2 {
            padding: 0 10px;
            box-sizing: border-box;
            width: 100%;
            height: 44px;
            border: 1px solid #DDDDDD;
            font-style: normal;
            font-weight: 400;
            font-size: 14px;
            line-height: 44px;
            display: flex;

            /* 333 */

            color: #333333;

            .dizhi {
                width: 250px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }

    .shuru {
        width: 100%;
        float: left;
        padding: 0 15px;
        box-sizing: border-box;
    }

    .tijiao {
        width: 100%;
        padding: 25px 15px;
        box-sizing: border-box;
        float: left;

        .tijiao2 {
            width: 100%;
            height: 44px;
            background: var(--main-color);
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            /* identical to box height */

            text-align: center;

            color: #FFFFFF;
        }
    }
}

.shangchaun {
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
<style>
.recharge.van-uploader__upload {
    width: 120px !important;
    height: 120px !important;
}
</style>
