<template>
    <div class="verify">
        <fx-header>
        </fx-header>
        <div class="content">
            <div class="title textColor">{{ $t('safeVertify') }}</div>
            <p v-if="currentType == 3">{{ $t('verifyGoogleTips') }}</p>
            <span class="label textColor">{{ currentType == 2 ? $t('emailVerify') : currentType == 1 ? $t('phoneVerify')
                    :
                    $t('googleVerify')
            }}</span>
            <p v-if="currentType == 2">{{ $t('verifyEmailTips', { 'account': account }) }}</p>
            <p v-if="currentType == 1">{{ $t('verifyPhoneTips', { 'account': account }) }}</p>
            <div class="iptbox inputBackground">
                <input type="text" class="inputBackground textColor" :placeholder="$t('entryVerifyCode')"
                    v-model="verifycode" @input="changeInput">
                <span v-if="currentType != 3" @click="senCode">{{ $t('reSendVerifyCode') }}<template v-if="time"> ({{
                        time
                }})s</template></span>
            </div>
            <van-button class="w-full" :disabled="!hightLight" style="margin-top:90px;" type="primary"
                @click="$router.push({ name: 'resetPassword', query: { type: currentType, account, verifycode, username } })">
                {{ $t('nextStep') }}
            </van-button>
            <!-- <button :disabled="!hightLight" class="btn"
                @click="$router.push({ name: 'resetPassword', query: { type: currentType, account, verifycode, username } })"
                :class="hightLight ? 'hightLight' : ''">{{ $t('nextStep')
                }}</button> -->
        </div>
    </div>
</template>

<script setup>
import { _sendVerifyCode } from "@/service/login.api";
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
const route = useRoute()

const verifycode = ref('')
const currentType = ref('')
const account = ref('')
const username = ref('')
const hightLight = ref(false)
const timer = ref(null)
const time = ref(0)

onMounted(() => {
    let type = route.query.type;
    currentType.value = type;
    account.value = route.query.account;
    username.value = route.query.username;
    if (currentType.value != 3) {
        clearTimer()
        senCode()
    }
})

const changeInput = () => {
    if (verifycode.value.length == 6) {
        hightLight.value = true;
    } else {
        hightLight.value = false;
    }
}
const senCode = () => {
    if (time.value > 0) {
        return false
    }
    _sendVerifyCode({
        target: account.value,
    }).then((res) => {
        time.value = 30;
        timer.value = setInterval(() => {
            if (time.value > 0) {
                time.value = time.value - 1
            } else {
                time.value = 0;
                clearTimer()
            }
        }, 1000);
    })
}
const clearTimer = () => {
    clearInterval(timer.value)
    timer.value = null
}
onUnmounted(() => {
    clearTimer()
})

</script>

<style lang="scss" scoped>
.verify {
    font-size: 13px;
}

.title {
    font-weight: 700;
    font-size: 26px;
    margin-top: 27px;
    margin-bottom: 17px;
}

.label {
    margin-top: 11px;
}

.content {
    padding: 0 16px;

    p {
        color: #868D9A;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .iptbox {
        height: 44px;
        margin-top: 8px;
        padding: 0 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 3px;

        input {
            flex: 1;
            height: 100%;
            border: none;
        }

        span {
            color: #1D91FF;
        }
    }
}
</style>