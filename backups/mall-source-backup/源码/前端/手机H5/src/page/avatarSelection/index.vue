<template>
    <div class="avatar_wrap">
        <van-nav-bar safe-area-inset-top fixed :title="$t('选择头像')" :right-text="$t('保存')" left-arrow @click-left="$router.go(-1)"
            @click-right="submitHandle" />
        <div style="width: 100%; height: 46px"></div>
        <div class="avatar_box">
            <div class="image" v-for="item of 20" :key="item">
                <img :src="require(`@/assets/image/avatar/${item}.png`)" @click="selectAvatar(item)" class="avatar" alt="">
                <div class="active" v-if="item == current">
                    <img src="@/assets/image/dui.png" class="icon" alt="">
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import { NavBar, Toast } from "vant";
import { apiRefreshAvatar } from "@/API/common";
export default {
    components: {
        [NavBar.name]: NavBar,
    },
    data() {
        return {
            current: 1
        }
    },
    mounted() {
        this.current = this.$route.query?.avatar || 1
    },
    methods: {
        selectAvatar(item) {
            this.current = item
            // this.$emit('selectAvatar', item)
        },
        async submitHandle() {
            Toast.loading({
                duration: 0,
                forbidClick: true,
                message: ""
            });
            await apiRefreshAvatar({ idx: this.current })
            Toast.clear();
            this.$router.go(-1)
        }
    }
}
</script>

<style lang="scss" scoped>
.avatar_box {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    padding: 30px 19px;

    .image {
        position: relative;
        border-radius: 50%;
        margin-right: 25px;
        margin-bottom: 25px;

        &:nth-child(4n) {
            margin-right: 0;
        }

        .active {
            width: 20px;
            height: 20px;
            background: var(--main-color);
            position: absolute;
            bottom: 2px;
            right: 2px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
            border: 1px solid #fff;

            .icon {
                width: 8px;
                height: 10px;
            }
        }
    }

    .avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;



    }
}
</style>