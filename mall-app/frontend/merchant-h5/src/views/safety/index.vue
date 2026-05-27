<template>
    <div class="safety">
        <fx-header :back="false" @back="$router.push('/my/index')">
        </fx-header>
        <div class="content">
            <div class="title textColor">{{ $t('safe') }}</div>
            <div class="tit1 textColor">{{ $t('twoFactorAuthentication') }}</div>
            <div class="tit2">{{ $t('twoAuthenticationTips') }}</div>
        </div>
        <van-grid :column-num="2" :gutter="12" class="verify">
            <van-grid-item v-for="(item, index) in verifyList" :key="index"
                @click="gotoVerify(item.url, item.isVerify, item.type)">
                <div class="verifyBox">
                    <div class="left">
                        <div class="imgBox">
                            <img v-if="item.isVerify" :src="item.icon.verify" alt="">
                            <img v-else :src="item.icon.verifyno" alt="">
                        </div>
                    </div>
                    <div class="right icon">
                        <img src="@/assets/image/userCenter/more.png" alt="">
                    </div>
                </div>
                <div class="name textColor">{{ item.title }}</div>
            </van-grid-item>
        </van-grid>
        <div class="content">
            <div v-for="(obj, index) in list" :key="index" @click="$router.push(obj.url)"
                class="flex justify-between items-center h-50">
                <div class="textColor">{{ obj.name }}</div>
                <div class="icon"><img src="@/assets/image/userCenter/more.png" alt=""></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { Grid, GridItem, Toast } from 'vant'
import { _getVerifTarget } from '@/service/user.api.js'
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
const router = useRouter()
const { t } = useI18n()

const verifyList = ref([
    {
        title: t('googleAuthenticator'),
        name: "google",
        icon: {
            verifyno: new URL('@/assets/image/userCenter/gooleVerifyno.png', import.meta.url),
            verify: new URL('@/assets/image/userCenter/gooleVerify.png', import.meta.url)
        },
        isVerify: false,
        url: '/bindVerify?type=3',
        type: 3
    },
    {
        title: t('phoneVerify'),
        name: "phone",
        icon: {
            verifyno: new URL('@/assets/image/userCenter/phoneVerifyno.png', import.meta.url),
            verify: new URL('@/assets/image/userCenter/phoneVerify.png', import.meta.url)
        },
        isVerify: false,
        url: '/bindVerify?type=1',
        type: 1
    },
    {
        title: t('emailVerify'),
        name: "email",
        icon: {
            verifyno: new URL('@/assets/image/userCenter/emialVerifyno.png', import.meta.url),
            verify: new URL('@/assets/image/userCenter/emialVerify.png', import.meta.url)
        },
        isVerify: false,
        url: '/bindVerify?type=2',
        type: 2
    }
])

const list = ref([
    {
        name: t('changeLoginPassword'),
        url: "/changePassword"
    },
    {
        name: t('changeFunsPassword'),
        url: "/changeFundsPassword"
    },
    {
        name: t('manualReset'),
        url: "/resetVerify?type=0"
    }
])

onMounted(() => {
    getVerifTarget()
})

const getVerifTarget = () => {
    _getVerifTarget({
    }).then((res) => {
        dataRest(res)
    })
}
const dataRest = (data) => {
    verifyList.value.forEach(item => {
        if (item.name == 'google') {
            item.isVerify = data.google_auth_bind;
        } else if (item.name == 'phone') {
            item.isVerify = data.phone_authority;
        } else if (item.name == 'email') {
            item.isVerify = data.email_authority;
        }
    })
}
const gotoVerify = (url, isVerify, type) => {
    if (isVerify) {
        router.push(`/changeVerify?type=${type}`);
    } else {
        router.push(url)
    }
}
</script>

<style lang="scss" scoped>
.safety {
    font-size: 12px;
    width: 100%;
    box-sizing: border-box;

    :deep(.van-grid-item__content) {
        background: #f6f6f6;
    }
}

.title {
    font-weight: 700;
    font-size: 26px;
    margin-top: 12px;
    margin-bottom: 12px;
}

.content {
    padding: 0 16px;
}

.tit1 {
    font-size: 15px;
    font-weight: 400;
}

.tit2 {
    color: #868D9A;
    font-size: 12px;
    margin-top: 5px;
}

.verify {
    font-size: 12px;
    color: #222832;
    margin-top: 21px;
    font-weight: 700;

    .verifyBox {
        display: flex;
        justify-content: space-between;
        padding-left: 14px;
        padding-right: 27px;
        box-sizing: border-box;
        align-items: center;
        width: 100%;

        .left {
            .imgBox {
                width: 45px;
                height: 34px;

                img {
                    width: 100%;
                    height: 100%;
                }
            }
        }
    }

    .name {
        width: 100%;
        padding-left: 14px;
        margin-top: 10px;
    }
}

.icon {
    width: 14px;
    height: 14px;

    img {
        width: 100%;
        height: 100%;
    }
}

.h-50 {
    height: 50px;
    ;
}
</style>