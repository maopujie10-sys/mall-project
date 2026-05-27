<template>
    <div class="complaint">
        <van-nav-bar safe-area-inset-top fixed :title="$t('投诉卖家')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>
        <el-form label-position="top" label-width="80px" :model="formData" :rules="rules" ref="ruleForm" class="acc_form">
            <el-form-item :label="$t('投诉类型')" prop="type">
                <el-select v-model="formData.type" :placeholder="$t('请选择投诉类型')">
                    <el-option v-for="type of complaintType" :key="type.value" :label="$t(type.label)" :value="type.value">
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item :label="$t('截图、凭证')" prop="images">
                <van-uploader v-model="formData.images" multiple />
            </el-form-item>
            <el-form-item :label="$t('投诉原因')" prop="reason">
                <el-input type="textarea" maxlength="1000" :autosize="{ minRows: 6, maxRows: 8 }"
                    v-model.trim="formData.reason"></el-input>
            </el-form-item>
        </el-form>
        <div class="sub_btn" @click="submitForm">{{ $t('提交') }}</div>
    </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { Uploader } from 'vant'

export default {
    components: {
        [Uploader.name]: Uploader
    },
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            formData: {
                reason: '',
                images: [],
                type: ''
            },
            complaintType: [
                {
                    label: '长时间不发货',
                    value: '1'
                },
                {
                    label: '卖家服务态度恶劣',
                    value: '2'
                },
                {
                    label: '卖家交易欺诈',
                    value: '3'
                },
                {
                    label: '卖家承诺不履行',
                    value: '4'
                },
                {
                    label: '其他',
                    value: '5'
                }
            ],
            pwtStatus: false,
            rules: {
                type: [
                    { required: true, message: this.$t('请选择投诉类型'), trigger: 'change' }
                ],
                reason: [
                    { required: true, message: this.$t('请选择投诉原因'), trigger: 'blur' }
                ],
                images: [
                    { required: true, message: this.$t('请上传截图、凭证'), trigger: 'change' }
                ]
            }
        }
    },

    computed: {
        ...mapGetters({
            userInfo: 'userInfo'
        })
    },
    methods: {
        onClickLeft() {
            this.$router.go(-1)
        },
        handleRemove(file, fileList) {
            console.log(file, fileList);
        },
        handlePictureCardPreview(file) {
            console.log(`file ::->`, file);
        },
        submitForm() {
            this.$refs.ruleForm.validate((valid) => {
                if (valid) {
                    alert('submit!');
                } else {
                    console.log('error submit!!');
                    return false;
                }
            });
        },
    }
}
</script>

<style lang="scss" scoped>
.acc_form {
    padding: 0 15px;

    :deep(.el-form-item__label) {
        padding: 0 !important;
        font-weight: 600;
        font-size: 16px;
        color: #333;
    }
}

:deep(.van-uploader__upload) {
    width: 105px !important;
    height: 105px !important;
}

:deep(.van-uploader__preview) {
    width: 105px !important;
    height: 105px !important;

    .van-image {
        width: 100%;
        height: 100%;
    }
}

.el-form-item {
    display: flex;
    flex-direction: column;
}

:deep(input) {
    padding-right: 60px;
}

.sub_btn {
    margin: 15px 15px;
    margin-top: 56px;
    background: var(--main-color);
    border-radius: 4px;
    height: 44px;
    font-style: normal;
    font-weight: 400;
    font-size: 16px;
    line-height: 44px;
    text-align: center;
    color: #FFFFFF;
}
</style>
<style lang="scss">
.van-dialog__message {
    padding-top: 20px;
    line-height: 25px;
    border: none;
}

.van-dialog__footer {
    padding: 0 15px 30px 15px;

    &::after {
        display: none;
    }

    button {
        border: none;
        border-radius: 8px;

        &:nth-child(1) {
            border: 1px solid #999999;
            margin-right: 10px;
        }

        &:nth-child(2) {
            background: #DA3231;
            color: #FFFFFF !important;
        }

        &::before {
            display: none;
        }

        &::after {
            display: none;
        }
    }
}

.el-select {
    width: 100% !important;
}
</style>