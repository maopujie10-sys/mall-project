<template>
    <div class="resetVerify">
        <fx-header>
            <template #title>
                {{ title }}
            </template>
        </fx-header>
        <div class="content">
            <div>
                <div class="textColor">{{ $t('uploadCredentPassport') }}</div>
                <div class="flex mt-4 mb-8 justify-between">
                    <div class="flex-1 flex flex-col text-center justify-center items-center">
                        <div class="upload-wrap">
                            <!-- <img :src="idcard_path_front_path" alt="" class="w-full imgShow" v-if="showImg1" /> -->
                            <van-uploader v-model="frontFile" multiple :max-count="1" :after-read="afterRead"
                                @click-upload="onClickUpload('frontFile')" />
                        </div>
                        <div class="mt-4 font-14 h-5 text-grey">{{ $t('credentFront') }}</div>
                    </div>
                    <div class="flex-1 flex flex-col text-center justify-center items-center">
                        <div class="upload-wrap">
                            <!-- <img :src="idcard_path_back_path" alt="" class="w-full imgShow" v-if="showImg2" /> -->
                            <van-uploader v-model="reverseFile" multiple :max-count="1" :after-read="afterRead"
                                @click-upload="onClickUpload('reverseFile')" />
                        </div>
                        <div class="mt-4 font-14 h-5 text-grey">{{ $t('credentObverse') }}</div>
                    </div>
                    <div class="flex-1 flex flex-col text-center justify-center items-center">
                        <div class="upload-wrap">
                            <!-- <img :src="idcard_path_hold_path" alt="" class="w-full imgShow" v-if="showImg3" /> -->
                            <van-uploader v-model="fileList" multiple :max-count="1" :after-read="afterRead"
                                @click-upload="onClickUpload('fileList')" />
                        </div>
                        <div class="mt-4 font-14 h-5 text-grey">{{ $t('handCredent') }}</div>
                    </div>
                </div>
            </div>
            <ExChecked class="mb-5" :list="list" @checkedSelect="onChecked"></ExChecked>
            <div v-if="currentType == 0">
                <ExInput :label="$t('fundsPassword')" :placeholderText="$t('fundsPasswordContTips')" v-model="password"
                    :tips="$t('funsPasswordTips')" typeText="password" />
                <ExInput :label="$t('confirmFundsPassword')" :placeholderText="$t('fundsPasswordContTips')"
                    v-model="repassword" :tips="$t('funsPasswordTips')" typeText="password" />
            </div>
            <ExInput :label="$t('message')" :placeholderText="$t('entryMessage')" v-model="remark" />
            <van-button class="w-full" style="margin-top:10px;" @click="submit" type="primary">
                {{ $t('submit') }}
            </van-button>
        </div>
    </div>
</template>

<script setup>
import ExInput from "@/components/ex-input/index.vue";
import ExChecked from "@/components/ex-checked/index.vue";
import { _uploadImage } from '@/service/upload.api'
import { _getSafewordApply, _setSafewordApply } from '@/service/user.api.js'
import { Uploader } from 'vant';
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter, useRoute } from "vue-router";
const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const title = ref('')
const remark = ref('')
const password = ref('')
const repassword = ref('')
const currentType = ref(0)
const list = ref([
    {
        name: t('resetFundsPassword'),
        type: 0
    },
    {
        name: t('resetPhone'),
        type: 1
    },
    {
        name: t('resetEmail'),
        type: 2
    },
    {
        name: t('resetGoogleVerify'),
        type: 3
    },
])
const frontFile = ref([])
const reverseFile = ref([])
const fileList = ref([])
const idcard_path_front_path = ref('')
const idcard_path_back_path = ref('')
const idcard_path_hold_path = ref('')
const curFile = ref('frontFile')
const status = ref('') // 0
const showImg1 = ref(false)
const showImg2 = ref(false)
const showImg3 = ref(false)


onMounted(() => {
    currentType.value = route.query.type;
    init(currentType.value);
    getSafewordApply();
})

const init = (type) => {
    if (type == 1) {
        title.value = t("artificialResetPhone");
    } else if (type == 2) {
        title.value = t("artificialResetEmail");
    } else if (type == 3) {
        title.value = t("artificialResetGoogleVerify");
    } else {
        title.value = t("artificialResetFundsPassword");
    }
}
const onChecked = (index) => {
    currentType.value = index - 1;
    console.log(currentType.value)
    init(currentType.value)
}
const afterRead = (file) => { /// 处理文件
    console.log(file);
    file.status = 'uploading'
    file.message = t('uploading')
    _uploadImage(file).then(data => {
        file.status = 'success';
        file.message = t('uploadSuccess');
        file.resURL = data
        if (curFile.value == 'frontFile') {
            frontFile.value = [file]
        } else if (curFile.value == 'reverseFile') {
            reverseFile.value = [file]
        } else {
            fileList.value = [file]
        }
    }).catch(err => {
        file.status = 'failed';
        file.message = t('uploadFailed');
    })
}
const onClickUpload = (type) => {
    console.log(type);
    curFile.value = type
}
const getSafewordApply = () => {
    _getSafewordApply({
    }).then((data) => {
        if (data.length != 0) {
            status.value = data[0].status;
            idcard_path_front_path.value = data[0].idcard_path_front_path
            idcard_path_back_path.value = data[0].idcard_path_back_path
            idcard_path_hold_path.value = data[0].idcard_path_hold_path
        }
    })
}
const setSafewordApply = () => {
    let operate;
    if (currentType.value == 0) {
        operate = 0
    } else if (currentType.value == 1) {
        operate = 2
    } else if (currentType.value == 2) {
        operate = 3
    } else if (currentType.value == 3) {
        operate = 1
    }
    _setSafewordApply({
        idcard_path_front: frontFile.value.length && frontFile.value[0].resURL || idcard_path_front_path.value || '',
        idcard_path_back: reverseFile.value.length && reverseFile.value[0].resURL || idcard_path_back_path.value || '',
        idcard_path_hold: fileList.value.length && fileList.value[0].resURL || idcard_path_back_path.value || '',
        operate: operate, //0 修改资金 1取消谷歌绑定 ，2取消手机绑定 3取消邮箱绑定
        safeword: password.value,
        safeword_confirm: repassword.value,
        remark: remark.value
    }).then((res) => {
        router.push({ name: 'resetSuccess', query: { type: currentType.value } })
    })
}
const submit = () => {
    setSafewordApply();

}


</script>

<style lang="scss" scoped>
.resetVerify {
    width: 100%;
    box-sizing: border-box;
}


.content {
    font-size: 13px;
    padding: 16px;
    border-top: 1px solid #E5E7ED;
}

.upload-wrap {
    width: 110px;
    height: 110px;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;

    img {
        height: 100%;
    }
}

.opacity0 {
    opacity: 0;
}

.opacity1 {
    opacity: 1;
}

.imgShow {
    top: 0;
    position: absolute;
}
</style>