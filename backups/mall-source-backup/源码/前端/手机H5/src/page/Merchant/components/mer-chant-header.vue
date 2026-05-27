<template>
    <div class="mer-chant-header">
        <div class="down-header">
            <router-link to="/" class="left">
                <img :src="logo" />
            </router-link>

            <div class="right">

                <el-dropdown @command="handleSetLang" :trigger="'click'">
                    <div class="cn-wrap">
                        <img class="cn-img" :src="languageIcon" />
                        <img class="down-img" src="@/assets/image/Merchant/down.png" />
                    </div>
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item :command="index" v-for="(item, index) in lang" :key="index">
                            <div class="lang-item">
                                <img :src="item.icon" />
                                {{ item.title }}
                            </div>
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
            </div>
        </div>
        <div class="content">
            <img src="@/assets/image/Merchant/image38.png" />
            <div class="content-text">
                <p class="title">{{ $t('商户入驻协议') }}</p>
                <p>{{ $t('招商政策全面升级诚商优质商') }}</p>
            </div>
        </div>
    </div>
</template>

<script>

import { DropdownMenu, DropdownItem, Dropdown } from 'element-ui'
import { mapGetters, mapMutations } from "vuex";
export default {
    name: 'mer-chant-header',
    data() {
        return {
            logo: require(`@/assets/${process.env.VUE_APP_ITEM_NAME}/logo.${this.$store.state.multiItem[process.env.VUE_APP_ITEM_NAME].suffix}`),
            lang: [
                {
                    title: '简体中文',
                    key: 'cn',
                    icon: require('@/assets/image/language/cn.png')
                },
                {
                    title: 'English',
                    key: 'en',
                    icon: require('@/assets/image/language/usa.png')
                },
                {
                    title: '繁体中文',
                    key: 'tw',
                    icon: require('@/assets/image/language/tw.png')
                }
            ],
        }
    },
    computed: {
        languageIcon() {
            const language = this.$store.getters.language || 'tw'
            const icon = {
                'cn': require('@/assets/image/language/cn.png'),
                'en': require('@/assets/image/language/usa.png'),
                'tw': require('@/assets/image/language/tw.png')
            }
            return icon[language]
        },
        ...mapGetters({
            activeLang: 'language'
        })
    },
    created() {

    },
    components: {
        [DropdownMenu.name]: DropdownMenu,
        [DropdownItem.name]: DropdownItem,
        [Dropdown.name]: Dropdown

    },
    methods: {
        ...mapMutations(['setLanguage']),
        handleSetLang(index) {
            console.log(index)
            // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
            this.$i18n.locale = this.lang[index].key
            // // 提交mutations
            this.setLanguage(this.lang[index].key)
        },
    }
}
</script>

<style lang="scss" scoped>
.mer-chant-header {
    background: #212121;
    font-size: 14Px;
    min-width: 1200Px;

    .down-header {
        height: 70Px;
        width: 1200Px;
        margin: 0 auto;
        display: flex;
        align-items: center;

        .left {
            flex: 1;
            cursor: pointer;

            img {
                height: 43Px;
            }
        }

        .right {
            display: flex;
            cursor: pointer;

            .cn-wrap {
                display: flex;
                align-items: center;

                .cn-img {
                    width: 20Px;
                    height: 20Px;
                }

                .down-img {
                    margin-left: 5Px;
                }

            }


        }
    }

    .content {
        width: 1200Px;
        margin: 0 auto;
        position: relative;
        padding-bottom: 100Px;

        img {
            width: 100%;
        }

        .content-text {
            width: 58%;
            position: absolute;
            top: 30%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;

            p {
                width: 100%;
                font-size: 24Px;
                color: rgba(166, 166, 166, 1);
            }

            .title {
                color: var(--main-color);
                font-size: 48Px;
                margin-bottom: 4Px;
            }
        }
    }
}

@media screen and (max-width:500Px) {
    .mer-chant-header {
        min-width: 100% !important;
        background: #212121;
        font-size: 14Px;

        .down-header {
            width: 100% !important;

            .left {
                padding-left: 15Px !important;
            }

            .right {
                padding-right: 15Px;
            }
        }

        .content {
            width: 92%;
            margin: 0 auto;
            position: relative;

            img {
                width: 100%;
            }

            .content-text {
                width: 58%;
                position: absolute;
                top: 13%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: flex-start;

                p {
                    width: 100%;
                    font-size: 12Px;
                    color: rgba(166, 166, 166, 1);
                }

                .title {
                    color: var(--main-color);
                    font-size: 14Px;
                }
            }
        }
    }
}

.lang-item {
    display: flex;
    align-items: center;

    img {
        width: 20Px;
        height: 20Px;
        margin-right: 5px;
    }
}
</style>
