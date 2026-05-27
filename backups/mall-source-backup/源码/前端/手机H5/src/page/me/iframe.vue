<template>
    <div class="iframe-main">
        <van-nav-bar safe-area-inset-top fixed :title="title" left-arrow @click-left="onClickLeft" />
        <iframe :src="url" scrolling="auto" frameborder="0" class="nq-ys iframe" @scroll.stop="false"></iframe>
    </div>
</template>

<script>
import { mapMutations } from 'vuex'
export default {
    //   name: "iframe",
    data() {
        return {
            itemName: process.env.VUE_APP_ITEM_NAME,
            url: "",
            title: "",
            paths: {
                'Argos': 'https://argos.me/',
                'MetaShop': 'https://e-metashop.com/',
                'Tongda': 'https://www.tongdashops.com/',
                'FamilyMart': 'https://familymartex.com/',
                'FamilyShop': 'https://www.familyshopit.com/',
                'Inchoi': 'https://Inchoishop.com/',
                'Hive': 'https://www.hivemalls.com/',
                'TikTokMall': 'https://tiktokmallit.com/',
                'Shop2u': 'https://shop2u.co/',
                'EShop': 'https://ml.thsjbvh.site/',
                'GreenMall': 'https://djeion.com/',
                'SM-wholesaleShop': 'https://justshopmall.com',
                'ArgosShop': 'https://argosshoppro.com',
                'Iceland': 'https://icelandmarts.com',
                'INT Overstock': 'https://overstock8.me',
                'TikTok-Wholesale': 'https://tiktok-wholesale.com/',
            }
        };
    },
    mounted() {
        if(this.title == '') {
            this.title = this.$route.query.title;
        }
        this.url = this.$route.query.url;
        window.addEventListener('message', (e) => {
            if (e.data?.lang && this.title == this.$t('商家入驻')) {
                if (e.data?.lang == 'en-US') {
                    this.$i18n.locale = 'en'
                    this.setLanguage('en');
                } else if (e.data?.lang == 'CN') {
                    this.$i18n.locale = 'tw'
                    this.setLanguage('tw');
                } else if (e.data?.lang == 'zh-CN') {
                    this.$i18n.locale = 'cn'
                    this.setLanguage('cn');
                } else {
                    this.$i18n.locale = e.data?.lang
                    this.setLanguage(e.data?.lang);
                }
                this.$nextTick(() => {
                    this.title = this.$t('商家入驻');
                })
            }

            if (e.data == 'jump') {
                if (window?.plus) {
                    plus.runtime.openURL(this.paths[this.itemName] + 'ww')
                    // location.href = location.origin + '/ww'
                } else {
                    window.open(location.origin + '/ww')
                }
            }
        });
    },
    methods: {
        ...mapMutations(["setLanguage"]),
        onClickLeft() {
            this.$router.go(-1);
        }
    }
}
</script>

<style scoped lang="scss">
.iframe-main {
    width: 100%;
    height: 100%;
    padding: 45px 0 0 0;
    overflow: hidden;

    .iframe {
        margin-top: 45px;
        width: 100%;
        height: 100%;
        -webkit-overflow-scrolling: touch;
        border: none;
        padding: 0;
        margin: 0;
        overflow: hidden;
    }
}
</style>