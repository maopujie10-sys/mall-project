<template>
    <div class="box" style="min-height: 100vh;">
        <div class="loading_wrap" v-show="showLoading" v-if="!['INT Overstock'].includes(itemName)">
            <div class="loader-box">
                <div class="loader">
                    <!-- <img class="logo" :src="require(`@/assets/logos/${itemName}.png`)" alt=""> -->
                    <div class="ele-animation">
                        <img :src="catIcon" width="1180" height="70">
                    </div>
                </div>
                <div class="lable">Loading...</div>

                <!-- <div class="animate">
                    <span v-for="(item, index) of 'Loading'">
                        {{ item }}
                    </span>
                    <span v-for="(item, index) of itemName">
                        {{ item }}
                    </span>
                </div> -->
            </div>
        </div>
        <div v-else class="loading_box" v-show="showLoading">
            <img :src="require(`@/assets/${itemName}/qidong.png`)" alt="">
        </div>
        <router-view></router-view>
        <div class="navbar">
            <v-navbar v-if="!isReload" :idx="idx" @change="change"></v-navbar>
        </div>
    </div>
</template>

<script>
import NavBar from "@/components/BottomNavigation"
export default {
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            idx: 0,
            showIconOrSrc: true,
            isReload: false,
            showLoading: true,
        }
    },
    components: {
        "v-navbar": NavBar,
    },
    computed: {
        catIcon() {
            if (['TikTok-Wholesale', 'TikTokMall'].includes(this.itemName)) {
                return require(`@/assets/${this.itemName}/car.png`)
            } else {
                return require('@/assets/image/car.png')
            }
        }
    },
    mounted() {
        // if (this.showLoading) {
        //     //获取dom节点
        //     var scrollTip = document.querySelector('.animate');
        //     //页面载入时，给它执行一次
        //     scrollTip.classList.add('three');
        //     //监听动画是否结束
        //     scrollTip.addEventListener('animationend', function () {
        //         //动画结束，移除动画的样式类
        //         scrollTip.classList.remove('three');
        //         //延时3秒，再将动画加入
        //         setTimeout(function () {
        //             scrollTip.classList.add('three');
        //         }, 2800)
        //     })
        // }
    },
    created() {
        if (!sessionStorage.getItem('showLoading')) {
            window.onload = () => {
                this.showLoading = false
            }
            const TIME = this.itemName == 'INT Overstock' ? 10000 : 15000
            if (this.showLoading) {
                setTimeout(() => {
                    this.showLoading = false
                }, TIME)
            }
        } else {
            this.showLoading = false
        }

        sessionStorage.setItem('showLoading', this.showLoading)
        if (this.$route.path == '/home') {
            this.idx = 0
        }
        if (this.$route.path == '/commodity') {
            this.idx = 1
        }
        if (this.$route.path == '/cart') {
            this.idx = 2
        }
        if (this.$route.path == '/me') {
            this.idx = 3
        }
        if (!localStorage.getItem('token')) {
            // TODO
            // this.$router.push({path:'/login'})
        }
    },
    methods: {
        change(index) {
            this.idx = index
        },
        handleReload() {
            this.isReload = true
            let time = setTimeout(() => {
                this.isReload = false
            }, 1200)
        }
    },
    watch: {
        '$route'(val) {
            if (val.path == '/home') {
                this.idx = 0
            }
            if (val.path == '/commodity') {
                this.idx = 1
            }
            if (val.path == '/cart') {
                this.idx = 2
            }
            if (val.path == '/me') {
                this.idx = 3
            }
            if (val.path == '/language') {
                // this.handleReload()
            }
        }
    },
}
</script>

<style scoped lang="scss">
.box {
    width: 100%;
    height: 100%;

}

.navbar {
    width: 100%;
    height: 56px;
    background: #fff;
    position: fixed;
    bottom: 0;
    z-index: 1999;
}

.loading_box {
    width: 100%;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 99999;
    display: flex;
    justify-content: center;
    align-items: center;

    img {
        width: 100%;
        height: 100%;
    }
}

.loading_wrap {
    width: 100%;
    height: 100vh;
    text-align: center;
    background-color: #fff;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 99999;

    .animate {
        font-size: 26px;
        margin: 10px 0 0;
    }

    .animate span {
        display: inline-block;
        color: var(--main-color);
    }



    .animate span:nth-of-type(2) {
        animation-delay: .1s;
    }

    .animate span:nth-of-type(3) {
        animation-delay: .15s;
    }

    .animate span:nth-of-type(4) {
        animation-delay: .2s;
    }

    .animate span:nth-of-type(5) {
        animation-delay: .25s;
    }

    .animate span:nth-of-type(6) {
        animation-delay: .3s;
    }

    .animate span:nth-of-type(7) {
        animation-delay: .35s;
    }

    .animate span:nth-of-type(8) {
        animation-delay: .4s;
    }

    .animate span:nth-of-type(9) {
        animation-delay: .45s;
    }

    .animate span:nth-of-type(10) {
        animation-delay: .5s;
    }

    .animate span:nth-of-type(11) {
        animation-delay: .55s;
    }

    .animate span:nth-of-type(12) {
        animation-delay: .6s;
    }

    .animate span:nth-of-type(13) {
        animation-delay: .65s;
    }

    .animate span:nth-of-type(14) {
        animation-delay: .7s;
    }

    .animate span:nth-of-type(15) {
        animation-delay: .75s;
    }

    .animate span:nth-of-type(16) {
        animation-delay: .8s;
    }

    .animate span:nth-of-type(17) {
        animation-delay: .85s;
    }

    .animate span:nth-of-type(18) {
        animation-delay: .9s;
    }

    .animate span:nth-of-type(19) {
        animation-delay: .95s;
    }

    .three span {
        color: var(--main-color);
        opacity: 0;
        transform: translate(-300px, 0) scale(0);
        animation: sideSlide 3s forwards;
    }

    @keyframes sideSlide {
        0% {
            transform: translate(-10px, 0) scale(.8);
            color: var(--main-color);
        }

        25% {
            transform: translate(10px, 0) scale(1);
            color: var(--main-color);
        }

        50% {
            transform: translate(-10px, 0) scale(1);
            color: var(--main-color);
        }

        75% {
            transform: translate(0) scale(1.2);
            color: #00f0ff;
        }

        100% {
            transform: translate(0) scale(1);
            opacity: 1;
            color: var(--main-color);
        }
    }



    .loader-box {
        width: 100%;
        height: 100vh;
        // padding: 200px 0;
        -moz-border-radius: 5px;
        -webkit-border-radius: 5px;
        border-radius: 5px;
        background-color: #ffffff;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transform: translateY(-30px);
    }

    .lable {
        height: 30px;
        line-height: 30px;
        font-family: Gotham, "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 20px;
        color: var(--main-color);
        transform: translateX(7px);
    }

    .loader {
        width: 90px;
        height: 90px;
        // background-color: #FFFFFF;
        overflow: hidden;
        display: block;
        -moz-border-radius: 100%;
        -webkit-border-radius: 100%;
        border-radius: 100%;
        border: 3px solid var(--main-color);
        position: relative;
        margin: 15px auto;
        z-index: 1;

        .logo {
            width: 90px;
            height: 90px;
            position: absolute;
            top: 0;
            left: 0;
            z-index: -1;
            opacity: .1;
        }
    }

    .ele-animation {
        animation: animationFrames linear 5s;
        animation-iteration-count: infinite;
        animation-fill-mode: forwards;
        /*when the spec is finished*/
        -webkit-animation: animationFrames linear 5s;
        -webkit-animation-iteration-count: infinite;
        -webkit-animation-fill-mode: forwards;
        /*Chrome 16+, Safari 4+*/
        -moz-animation: animationFrames linear 5s;
        -moz-animation-iteration-count: infinite;
        -moz-animation-fill-mode: forwards;
        /*FF 5+*/
        -o-animation: animationFrames linear 5s;
        -o-animation-iteration-count: infinite;
        -o-animation-fill-mode: forwards;
        /*Not implemented yet*/
        -ms-animation: animationFrames linear 5s;
        -ms-animation-iteration-count: infinite;
        -ms-animation-fill-mode: forwards;
        /*IE 10+*/
    }
}

@keyframes move {

    0% {

        left: 0;

        opacity: 0;

    }

    35% {

        left: 41%;

        -moz-transform: rotate(0deg);

        -webkit-transform: rotate(0deg);

        -o-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    65% {

        left: 59%;

        -moz-transform: rotate(0deg);

        -webkit-transform: rotate(0deg);

        -o-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    100% {

        left: 100%;

        -moz-transform: rotate(-180deg);

        -webkit-transform: rotate(-180deg);

        -o-transform: rotate(-180deg);

        transform: rotate(-180deg);

        opacity: 0;

    }

}



@-moz-keyframes move {

    0% {

        left: 0;

        opacity: 0;

    }

    35% {

        left: 41%;

        -moz-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    65% {

        left: 59%;

        -moz-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    100% {

        left: 100%;

        -moz-transform: rotate(-180deg);

        transform: rotate(-180deg);

        opacity: 0;

    }

}



@-webkit-keyframes move {

    0% {

        left: 0;

        opacity: 0;

    }

    35% {

        left: 41%;

        -webkit-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    65% {

        left: 59%;

        -webkit-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    100% {

        left: 100%;

        -webkit-transform: rotate(-180deg);

        transform: rotate(-180deg);

        opacity: 0;

    }

}



@-o-keyframes move {

    0% {

        left: 0;

        opacity: 0;

    }

    35% {

        left: 41%;

        -o-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    65% {

        left: 59%;

        -o-transform: rotate(0deg);

        transform: rotate(0deg);

        opacity: 1;

    }

    100% {

        left: 100%;

        -o-transform: rotate(-180deg);

        transform: rotate(-180deg);

        opacity: 0;

    }

}

@keyframes animationFrames {
    0% {
        transform: translate(-1160px, 15px);
    }

    100% {
        transform: translate(0px, 15px);
    }
}

@-moz-keyframes animationFrames {
    0% {
        transform: translate(-1160px, 15px);
    }

    100% {
        transform: translate(0px, 15px);
    }
}

@-webkit-keyframes animationFrames {
    0% {
        transform: translate(-1160px, 15px);
    }

    100% {
        transform: translate(0px, 15px);
    }
}

@-o-keyframes animationFrames {
    0% {
        transform: translate(-1160px, 15px);
    }

    100% {
        transform: translate(-0px, 15px);
    }
}

@-ms-keyframes animationFrames {
    0% {
        transform: translate(-1160px, 15px);
    }

    100% {
        transform: translate(0px, 15px);
    }
}</style>
