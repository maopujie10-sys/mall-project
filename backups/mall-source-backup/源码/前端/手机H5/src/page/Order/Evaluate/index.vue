<template>
    <div class="page-content">
        <van-nav-bar safe-area-inset-top fixed :title="$t('评价')" left-arrow @click-left="() => $router.back()" />
        <div style="width: 100%; height: 46px;" />

        <div v-if="goodsData.length" class="evaluate-content">
            <div v-for="(item, index) in goodsData" :key="index" class="item">
                <div class="goods-info">
                    <div class="poster">
                        <img :src="item.goodsIcon" alt="">
                    </div>
                    <div class="info">
                        <p class="name">{{ item.goodsName?.length > 27 ? (item.goodsName.slice(0, 27) + '...') :
                            item.goodsName }}</p>
                        <p class="price">$ {{ priceFormat(item.goodsReal) }}</p>
                        <van-rate class="rate-wrap" v-model="item.rating" :size="15" ::color="mainColor" void-icon="star"
                            void-color="#D9D9D9" />
                    </div>
                </div>
                <el-input type="textarea" :autosize="{ minRows: 3, maxRows: 4 }" :placeholder="$t('请输入评价信息')" resize="none"
                    v-model="item.content" maxlength="1000" show-word-limit />
                <div class="evaluate-title">{{ $t('评价晒图') }}</div>
                <van-uploader :after-read="afterRead" v-model="item.fileList" :name="index" :max-count="9" accept=".png,.jpg,.jpeg" />
            </div>

            <div class="submit-btn" @click="submitHandle">{{ $t('提交评论') }}</div>

        </div>
    </div>
</template>

<script>
import { NavBar, Toast, Rate, Uploader } from 'vant'

import {
    orderListGoods,
    orderEvaluationAdd
} from '@/API/user'

import {
    priceFormat
} from '@/utils/utis'
import { uploadimg } from "@/API/commodity";
export default {
    name: 'OrderEvaluate',
    components: {
        [NavBar.name]: NavBar,
        [Toast.name]: Toast,
        [Rate.name]: Rate,
        [Uploader.name]: Uploader
    },
    data() {
        return {
            mainColor: process.env.VUE_APP_MAIN_COLOR,
            fileList: [],
            cancelShow: false,
            remindShow: false,
            currentData: null,
            orderId: null,
            goodsData: []
        }
    },
    mounted() {
        this.$nextTick(() => {
            const { id } = this.$route.query
            if (id) {
                this.orderId = id
                this.getOrderGoods()
            } else {
                Toast(this.$t('订单号不存在'))
                setTimeout(() => {
                    this.$router.back()
                }, 1500);
            }
        })
    },
    methods: {
        afterRead(file, { name }) {
            // if('[object Array]' == Object.prototype.toString.call(file)) {
                
            // }
            let index = this.goodsData[name].fileList.length // 图片的索引
            Toast.loading({
                duration: 0,
                message: this.$t('上传中'),
                forbidClick: true,
            })
            let formData = new FormData();//通过formdata上传
            formData.append('file', file.file)
            formData.append('moduleName', 'selle')
            let goodsId = ''
            uploadimg(formData).then((data) => {
                console.log('图片上传成功', data)
                // this.ruleForm.idimg_2 = data
                this.goodsData[name][`imgUrl${index}`] = data //待提交图片的索引
            }).catch((error) => {
                this.fileList = [];
                // Toast.fail(this.$t('上传失败'));
                this.$notify(this.$t('上传失败'))
            }).finally(() => {
                Toast.clear()
            })
        },
        priceFormat(num) {
            return priceFormat(num)
        },
        getOrderGoods() {
            Toast.loading({
                duration: 0,
                message: this.$t('请求中'),
                forbidClick: true
            })

            orderListGoods({
                orderId: this.orderId
            }).then(res => {
                const data = res.pageList || []
                data.forEach(item => {
                    item.rating = 5
                    item.content = ''
                })
                this.goodsData = data
                Toast.clear()
            }).catch(() => {
                Toast.clear()
            })
        },

        async submitHandle() {
            const dataArr = this.goodsData.map(item => {
                const { rating, content, goodsId } = item
                let evaluationType = '1'
                if (rating < 2) {
                    evaluationType = '3'
                } else if (rating < 4) {
                    evaluationType = '2'
                } else {
                    evaluationType = '1'
                }
                let obj = {
                    orderId: this.orderId,
                    sellerGoodsId: goodsId,
                    rating,
                    content,
                    evaluationType
                }
                Object.keys(item).forEach(key => {
                    if (key.indexOf('imgUrl') !== -1) {
                        obj[key] = item[key]
                    }
                })
                return obj
            })
            Toast.loading({
                duration: 0,
                message: this.$t('提交中'),
                forbidClick: true,
            })

            for (let i = 0; i < dataArr.length; i++) {
                await orderEvaluationAdd(dataArr[i])
            }

            Toast.success(this.$t('成功'))
            setTimeout(() => {
                this.$router.back()
            }, 1000)
        }
    }
}
</script>

<style lang="scss" scoped>
.evaluate-title {
    font-size: 12px;
    color: #999999;
    margin-top: 18px;
    margin-bottom: 10px;
}

.page-content {
    min-height: 100vh;
    background-color: #F5F5F7;

    * {
        box-sizing: border-box;
    }

    /deep/ .el-textarea {
        textarea:focus {
            border-color: var(--main-color) !important;
        }
    }

    .evaluate-content {
        padding: 0 15px;
        padding-bottom: 40px;

        >.item {
            padding: 18px 24px;
            background-color: #fff;
            margin-top: 10px;

            >.goods-info {
                display: flex;
                padding-bottom: 15px;

                >.poster {
                    width: 78px;
                    height: 78px;
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: center;

                    >img {
                        width: 100%;
                        height: auto;
                    }
                }

                >.info {
                    padding-left: 15px;
                    flex: 1;

                    >.name {
                        overflow: hidden;
                        text-overflow: ellipsis;
                        display: -webkit-box;
                        -webkit-box-orient: vertical;
                        -moz-box-orient: vertical;
                        box-orient: vertical;
                        -webkit-line-clamp: 2;
                        line-clamp: 2;
                        font-size: 14px;
                        color: #000;
                    }

                    >.price {
                        display: flex;
                        align-items: center;
                        margin-top: 10px;
                        
                        color: var(--main-color);
                        font-size: 16px;
                        font-weight: bold;
                    }
                }
            }
        }

        >.submit-btn {
            margin-top: 40px;
            width: 100%;
            height: 44px;
            background: var(--main-color);
            border-radius: 4px;
            font-style: normal;
            font-weight: 400;
            font-size: 16px;
            line-height: 44px;
            text-align: center;
            color: #FFFFFF;
        }
    }
}
</style>
