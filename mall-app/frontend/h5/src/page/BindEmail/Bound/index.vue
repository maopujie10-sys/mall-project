<template>
    <div class="page-content">
        <van-nav-bar safe-area-inset-top fixed :title="$t('邮箱验证')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%;" class="h46"></div>

        <div class="bound-content">
            <img :src="boundImg" alt="" />
            <p>{{ $t('邮箱验证将保护您的账号和提现功能') }}</p>
            <div class="btn" @click="gotoReset">{{ $t('重置邮箱验证') }}</div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'BindEmailBound',
    data() {
        return {
            boundImg: require('@/assets/image/me/bound_email.png')
        }
    },
    methods: {
        onClickLeft() {
            this.$router.push('/Setting')
        },
        gotoReset() {
            this.$router.push('/BindEmail')
        }
    }
}
</script>

<style lang="scss" scoped>
.page-content {
    * {
        box-sizing: border-box;
    }

    .bound-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 15px;

        >img {
            width: 83px;
            height: 83px;
            margin-top: 25px;
        }

        >p {
            margin-top: 24px;
            color: #999;
            text-align: center;
            font-size: 12px;
            line-height: 17px;
        }

        >.btn {
            margin-top: 50px;
            width: 345px;
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
