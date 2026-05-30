<template>
    <div class="changeVerify">
        <fx-header>
            <template #title>
                {{ title }}
            </template>
        </fx-header>
        <div class="content">
            <div class="imgBox">
                <img v-if="currentType == 2" src="@/assets/image/userCenter/emailVerity.png" alt="" />
                <img v-if="currentType == 1" src="@/assets/image/userCenter/phoneVerity.png" alt="" />
                <img v-if="currentType == 3" src="@/assets/image/userCenter/googleVerity.png" alt="" />
            </div>
            <p>{{ currentType == 1 ? $t('phoneVerify') : currentType == 2 ? $t('emailVerify') :
                    $t('googleAuthApp')
            }}{{ $t('protectAccount') }}</p>
            <van-button class="w-full btn-content" type="primary" @click="goChange">
                {{ currentType == 1 ? $t('changePhoneVertify') : currentType == 2 ? $t('changeEmailVertify')
        : $t('changeGoogleVertify')
                }}
            </van-button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const title = ref('')
const currentType = ref('')

onMounted(() => {
    init()
})

const init = () => {
    let type = route.query.type;
    currentType.value = type;
    if (type == 1) {
        title.value = t("phoneVerify");
    } else if (type == 2) {
        title.value = t("emailVerify");
    } else if (type == 3) {
        title.value = t("googleVertifyBind");
    }
}
const goChange = () => {
    router.push({ name: 'resetVerify', query: { type: currentType.value } })
}

</script>

<style lang="scss" scoped>
.changeVerify {
    width: 100%;
    box-sizing: border-box;
}


.content {
    font-size: 13px;
    padding: 0 16px;
    margin-top: 30px;
    text-align: center;
}

.imgBox {
    width: 88px;
    height: 88px;
    margin: auto;

    img {
        width: 100%;
        height: 100%;
    }
}

p {
    color: #868C9A;
    font-size: 14px;
    margin-top: 22px;
}

.btn-content {
    margin-top: 10px;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
}
</style>