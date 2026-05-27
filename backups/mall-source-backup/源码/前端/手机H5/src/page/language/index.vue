<template>
    <div class="CommonProblem" style="min-height: 100vh;">
        <van-nav-bar safe-area-inset-top fixed :title="$t('语言设置')" left-arrow @click-left="onClickLeft" />
        <div style="width: 100%; height: 46px"></div>
        <div class="language-content">
            <div v-for="(item, index) in lang" :key="index" class="item" @click="handleSetLang(item.key, index)">
                <div class="content">
                    <img :src="item.icon" alt="" class="nation" />
                    <div class="title">{{ item.title }}</div>
                </div>
                <img v-if="item.key == $i18n.locale" :src="checkIcon" alt="" class="check" />
            </div>
        </div>
    </div>
</template>
<script>
import { mapGetters, mapMutations } from "vuex";
/**
 * 中文简体(cn)   中文繁体(tw)   英语(en)   德语(de)   法语(fr)   日语(ja)   韩语(ko)   马来西亚语(ms)   
 * 泰国语(th)   葡萄牙语(pt)   西班牙语(es)   俄语(ru)   希腊语(el)   意大利语(it)   土耳其语(tr)   
 * 南非荷兰语(af)
 * 
 * 意大利。德语。 马来西亚语  葡萄牙语  西班牙语  俄语  希腊语  土耳其语  法语
 * ['it', 'de', 'ms', 'pt', 'es', 'ru', 'el', 'tr', 'fr']
 */
export default {
    data() {
        return {
            lang: [
                {
                    title: "English",
                    key: "en",
                    icon: require("@/assets/image/language/usa.png"),
                },
                {
                    title: "Deutsch",
                    key: "de",
                    icon: require("@/assets/image/language/de.png"),
                },
                {
                    title: "français",
                    key: "fr",
                    icon: require("@/assets/image/language/fr.png"),
                },
                {
                    title: "Русский",
                    key: "ru",
                    icon: require("@/assets/image/language/ru.png"),
                },
                {
                    title: "Español",
                    key: "es",
                    icon: require("@/assets/image/language/es.png"),
                },
                {
                    title: "Português",
                    key: "pt",
                    icon: require("@/assets/image/language/pt.png"),
                },
                {
                    title: "Italiano",
                    key: "it",
                    icon: require("@/assets/image/language/it.png"),
                },
                {
                    title: "Melayu",
                    key: "ms",
                    icon: require("@/assets/image/language/ms.png"),
                },
                {
                    title: "Afrikaans",
                    key: "af",
                    icon: require("@/assets/image/language/af.png"),
                },
                {
                    title: "Ελληνικά",
                    key: "el",
                    icon: require("@/assets/image/language/el.png"),
                },
                {
                    title: "繁體中文",
                    key: "tw",
                    icon: require("@/assets/image/language/tw.png"),
                },
                {
                    title: "简体中文",
                    key: "cn",
                    icon: require("@/assets/image/language/cn.png"),
                },
                {
                    title: "Türkçe",
                    key: "tr",
                    icon: require("@/assets/image/language/tr.png"),
                },

                {
                    title: "日本語",
                    key: "ja",
                    icon: require("@/assets/image/language/ja.png"),
                },
                {
                    title: "한국어",
                    key: "ko",
                    icon: require("@/assets/image/language/ko.png"),
                },
                {
                    title: "ภาษาไทย",
                    key: "th",
                    icon: require("@/assets/image/language/th.png"),
                },
                {
                    title: "Filipino",
                    key: "ph",
                    icon: require("@/assets/image/language/ph.png"),
                },
                {
                    title: "عربي",
                    key: "ar",
                    icon: require("@/assets/image/language/ar.png"),
                },
                {
                    title: "Tiếng Việt",
                    key: "vi",
                    icon: require("@/assets/image/language/vi.png"),
                },
                {
                    title: "हिंदी",
                    key: "hi",
                    icon: require("@/assets/image/language/hi.png"),
                },
                {
                    title: "bahasa Indonesia",
                    key: "id",
                    icon: require("@/assets/image/language/id.png"),
                },

            ],
            handicapName: process.env.VUE_APP_ITEM_NAME,
            checkIcon: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/check.png`),
        };
    },
    mounted() {
        if (this.handicapName == 'Mbuy') {
            this.lang = this.lang.filter(item => (item.key != 'cn' && item.key != 'tw'))
        }
    },
    computed: {
        ...mapGetters({
            activeLang: "language",
        }),
    },
    methods: {
        ...mapMutations(["setLanguage"]),
        handleSetLang(lang, index) {
            // if(index > 2) return this.$notify(this.$t('暂不支持该语言'))
            // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
            this.$i18n.locale = lang;
            // 提交mutations
            this.setLanguage(lang);
            if (lang == 'ar') {
                document.documentElement.setAttribute('dir', 'rtl');

            } else {
                document.documentElement.setAttribute('dir', 'ltr');
            }
            this.$router.go(-1);
        },
        onClickLeft() {
            // console.log(this.$i18n.locale)
            
            this.$router.go(-1);
        },
    },
};
</script>
<style lang="scss" scoped>
.language-content {
    >.item {
        box-sizing: border-box;
        width: 100%;
        height: 50px;
        padding: 0 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #fff;
        border-bottom: 1px solid #eee;

        &:last-child {
            border-bottom: none;
        }

        >.content {
            display: flex;

            >.nation {
                width: 18px;
                height: 18px;
                border-radius: 50%;
                box-shadow: 0px 0px 1px rgba(0, 0, 0, .5);
            }

            >.title {
                font-size: 14px;
                color: #333;
                margin-left: 11px;
            }
        }

        >.check {
            width: 12px;
            height: 15px;
        }
    }
}
</style>
