<template>
    <div class="resetSuccess">
        <fx-header :back="false" @back="$router.push('/my/index')">
            <template #title>
                {{ title }}
            </template>
        </fx-header>
        <div class="content">
            <div class="imgBox"><img src="@/assets/image/success.png" alt="" /></div>
            <div class="styleFont">{{ $t('submitSuccess') }}</div>
            <div class="text-grey mt-2">{{ $t('dataUploadedSuccessfully') }}!</div>
            <div class="text-grey mt-11">{{ $t('moderatedTips') }}</div>
            <van-button class="w-full btn-content" @click="$router.push('/quotes/index')" type="primary">
                {{ $t('back') }}
            </van-button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
const { t } = useI18n()
const route = useRoute()

const title = ref('')

onMounted(() => {
    let type = route.query.type;
    init(type);
})
const init = (type) => {
    if (type == 1) {
        title.value = t("重置手机号");
    } else if (type == 2) {
        title.value = t("重置邮箱");
    } else if (type == 3) {
        title.value = t("重置谷歌验证");
    } else {
        title.value = t("重置资金密码");
    }
}
</script>

<style lang="scss" scoped>
.resetSuccess {
    width: 100%;
    box-sizing: border-box;
}

.content {
    font-size: 12px;
    padding: 16px;
    text-align: center;
}

.imgBox {
    width: 62px;
    height: 62px;
    margin: auto;

    img {
        width: 100%;
        height: 100%;
    }
}

.styleFont {
    margin-top: 24px;
    font-weight: 700;
    font-size: 28px;
}

.btn-content {
    margin-top: 10px;
    background-color: var(--site-main-color);
    border-color: var(--site-main-color);
}
</style>