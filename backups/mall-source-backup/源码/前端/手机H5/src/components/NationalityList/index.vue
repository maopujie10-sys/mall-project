<template>
    <div class="nationList">
        <van-action-sheet v-model="isShow" :title="title">
            <van-search v-if="isCode" class="inputBackground" v-model="val" :placeholder="$t('请输入要搜索的国家名称')"
                @input="onSearch(val)" @clear="onClear" />
            <div class="nation-item" v-for="(item, key) in countriesFind" :key="key" @click="selectItem(item, key)">
                <div class="iti-flag img" :class="key"></div>
                <div class="name">{{ item.name }}</div>
                <div class="code" v-if="isCode">{{ item.dialCode }}</div>
            </div>
            <van-empty v-if="Object.keys(countriesFind).length === 0" :description="$t('暂无数据')" />
            <!-- <div class="flex pl-30 pr-30 pt-30 pb-30 justify-between list-view box-border textColor"
        style="height: 50px; box-sizing: border-box;" v-for="(item,key) in countriesFind" :key="key"
        @click="selectItem(item,key)">
        <div class="flex items-center item-content">
          <div class="iti-flag mr-20" :class="key" style="transform: scale(2.1)"></div>
          <div class="name">{{ item.name }}</div>
        </div>
        <span>{{ item.dialCode }}</span>
      </div> -->
        </van-action-sheet>
    </div>
</template>

<script>
import { ActionSheet, Search, Empty } from 'vant';
import countries from './countryList';
export default {
    name: "nationalityList",
    components: {
        [ActionSheet.name]: ActionSheet,
        [Search.name]: Search,
        [Empty.name]: Empty,
    },
    props: {
        title: {
            type: String,
            default: ""
        },
        isCode: {
            type: Boolean,
            default: true
        },
        isInit: {
            type: Boolean,
            default: true
        }
    },
    data() {
        return {
            language: "en",
            isShow: false,
            //搜索值
            val: '',
            //国籍列表
            list: [],
            countries,
            countriesFind: {},
            selectIndex: 0,
            //简体中文国籍
            countryCodeList: ['93', '355', '213', '684', '376', '244',
                '1264', '1268', '54', '374', '297', '61', '43', '994', '1242',
                '973', '880', '1246', '375', '32',
                '501', '229', '1441', '975', '591', '387', '267', '55', '673', '359', '226', '257', '855', '237',
                '1', '238', '1345', '236', '235', '56', '86', '57', '269', '242', '243', '682', '506',
                '225', '385', '53', '357', '420', '45', '253', '1767', '1890', '971', '593', '20',
                '503', '240', '291', '372', '251', '500', '298', '679', '358', '33', '594', '689',
                '241', '220', '995', '49', '233', '350', '30', '299', '1809',
                '590', '671', '502',
                '44', '675', '245', '592', '509', '504', '852', '36', '354', '91', '62', '98', '964',
                '353', '44', '972', '39', '1876', '81', '44', '962', '7', '254', '850',
                '82', '381', '965', '996', '856', '371', '961', '266', '231', '218', '423', '370', '352',
                '853', '389', '261', '265', '60', '960', '223', '356', '596', '222', '230',
                '52', '373', '377', '976', '382', '1664', '212', '258', '95', '264', '977', '31', '599',
                '687', '64', '505', '227', '234', '47', '968', '92', '680', '507', '675',
                '595', '51', '63', '48', '351', '1787', '970',
                '974', '262', '40', '7', '250', '1869', '1758', '1784',
                '684', '378', '966', '221', '381', '248', '232', '65', '421', '386',
                '677', '252', '27', '211', '34', '94', '249', '597', '268', '46', '41', '963', '886', '992', '255',
                '66', '670', '228', '676', '1809', '216', '90', '993', '1649',
                '256', '380', '971', '44', '1', '598', '998', '678', '58', '84', '1340', '967', '260',
                '263'
            ],
            countryCnList: ['阿富汗', '阿尔巴尼亚', '阿尔及利亚', '美属萨摩亚',
                '安道尔', '安哥拉', '安圭拉岛', '安提瓜和巴布达', '阿根廷',
                '亚美尼亚', '阿鲁巴', '澳大利亚', '奥地利', '阿塞拜疆',
                '巴哈马群岛', '巴林', '孟加拉共和国', '巴巴多斯', '白俄罗斯',
                '比利时', '伯利兹', '贝宁', '百慕大群岛', '不丹', '玻利维亚', '波黑(波斯尼亚和黑塞哥维那)',
                '博茨瓦纳', '巴西', '文莱达鲁萨兰国', '保加利亚',
                '布基纳法索', '布隆迪', '柬埔寨', '喀麦隆', '加拿大', '佛得角', '开曼群岛', '中非共和国',
                '乍得', '智利', '中国', '哥伦比亚', '科摩罗', '刚果', '刚果民主共和国', '库克群岛', '哥斯达黎加', '科特迪瓦',
                '克罗地亚', '古巴', '塞浦路斯', '捷克共和国', '丹麦', '吉布提', '多米尼克', '多米尼加共和国', '迪拜',
                '厄瓜多尔',
                '埃及', '萨尔瓦多', '赤道几内亚', '厄立特里亚', '爱沙尼亚', '埃塞俄比亚', '福克兰群岛', '法罗群岛', '斐济',
                '芬兰', '法国', '法属圭亚那', '法属玻利尼西亚', '加蓬', '冈比亚', '格鲁吉亚', '德国', '加纳',
                '直布罗陀', '希腊', '格陵兰岛', '格林纳达', '瓜德罗普', '关岛', '危地马拉', '根西', '几内亚',
                '几内亚比绍共和国', '圭亚那', '海地', '洪都拉斯', '中国香港', '匈牙利', '冰岛', '印度', '印度尼西亚', '伊朗',
                '伊拉克', '爱尔兰', '马恩', '以色列', '意大利', '牙买加', '日本', '泽西',
                '约旦', '哈萨克斯坦', '肯尼亚', '朝鲜', '韩国', '科索沃', '科威特', '吉尔吉斯斯坦', '老挝人民民主共和国',
                '拉脱维亚', '黎巴嫩', '莱索托', '利比里亚', '利比亚', '列支敦斯登', '立陶宛', '卢森堡', '中国澳门',
                '马其顿王国', '马达加斯加', '马拉维', '马来西亚', '马尔代夫', '马里', '马耳他', '马提尼克', '毛里塔尼亚',
                '毛里求斯', '墨西哥', '摩尔多瓦', '摩纳哥', '蒙古', '黑山共和国', '蒙特塞拉特岛',
                '摩洛哥', '莫桑比克', '缅甸', '纳米比亚', '尼泊尔', '荷兰', '荷属安的列斯群岛', '新喀里多尼亚',
                '新西兰', '尼加拉瓜', '尼日尔', '尼日利亚', '挪威', '阿曼', '巴基斯坦', '帕劳', '巴拿马', '巴布亚新几内亚',
                '巴拉圭', '秘鲁', '菲律宾', '波兰', '葡萄牙', '波多黎各', '巴勒斯坦',
                '卡塔尔', '留尼旺', '罗马尼亚', '俄罗斯联邦', '卢旺达', '圣基茨和尼维斯', '圣卢西亚岛', '圣文森特和格林纳丁斯',
                '萨摩亚群岛', '圣马力诺', '沙特阿拉伯', '塞内加尔', '塞尔维亚', '塞舌尔', '塞拉利昂', '新加坡',
                '斯洛伐克', '斯洛文尼亚', '所罗门群岛', '索马里', '南非', '南苏丹', '西班牙', '斯里兰卡',
                '苏丹', '苏里南', '斯威士兰', '瑞典', '瑞士', '阿拉伯叙利亚共和国', '中国台湾', '塔吉克斯坦', '坦桑尼亚', '泰国',
                '东帝汶', '多哥', '汤加', '特立尼达和多巴哥', '突尼斯', '土耳其', '土库曼斯坦', '特克斯和凯科斯群岛',
                '乌干达', '乌克兰', '阿拉伯联合酋长国', '英国', '美国', '乌拉圭',
                '乌兹别克斯坦', '瓦努阿图', '委内瑞拉', '越南', '英属维尔京群岛', '也门',
                '赞比亚', '津巴布韦'
            ],
            countryFnList: ['阿富汗', '阿爾巴尼亞', '阿爾及利亞', '美屬薩摩亞',
                '安道爾', '安哥拉', '安圭拉島', '安提瓜和巴布達', '阿根廷',
                '亞美尼亞', '阿魯巴', '澳大利亞', '奧地利', '阿塞拜疆',
                '巴哈馬群島', '巴林', '孟加拉共和國', '巴巴多斯', '白俄羅斯',
                '比利時', '伯利茲', '貝寧', '百慕大群島', '不丹', '玻利維亞', '波黑(波斯尼亞和黑塞哥維那)',
                '博茨瓦納', '巴西', '文萊達魯薩蘭國', '保加利亞',
                '布基納法索', '布隆迪', '柬埔寨', '喀麥隆', '加拿大', '佛得角', '開曼群島', '中非共和國',
                '乍得', '智利', '中國', '哥倫比亞', '科摩羅', '剛果', '剛果民主共和國', '庫克群島', '哥斯達黎加', '科特迪瓦',
                '克羅地亞', '古巴', '塞浦路斯', '捷克共和國', '丹麥', '吉布提', '多米尼克', '多米尼加共和國', '迪拜',
                '厄瓜多爾',
                '埃及', '薩爾瓦多', '赤道幾內亞', '厄立特里亞', '愛沙尼亞', '埃塞俄比亞', '福克蘭群島', '法羅群島', '斐濟',
                '芬蘭', '法國', '法屬圭亞那', '法屬玻利尼西亞', '加蓬', '岡比亞', '格魯吉亞', '德國', '加納',
                '直布羅陀', '希臘', '格陵蘭島', '格林納達', '瓜德羅普', '關島', '危地馬拉', '根西', '幾內亞',
                '幾內亞比紹共和國', '圭亞那', '海地', '洪都拉斯', '中國香港', '匈牙利', '冰島', '印度', '印度尼西亞', '伊朗',
                '伊拉克', '愛爾蘭', '馬恩', '以色列', '意大利', '牙買加', '日本', '澤西',
                '約旦', '哈薩克斯坦', '肯尼亞', '朝鮮', '韓國', '科索沃', '科威特', '吉爾吉斯斯坦', '老撾人民民主共和國',
                '拉脫維亞', '黎巴嫩', '萊索托', '利比里亞', '利比亞', '列支敦斯登', '立陶宛', '盧森堡', '中國澳門',
                '馬其頓王國', '馬達加斯加', '馬拉維', '馬來西亞', '馬爾代夫', '馬里', '馬耳他', '馬提尼克', '毛里塔尼亞',
                '毛里求斯', '墨西哥', '摩爾多瓦', '摩納哥', '蒙古', '黑山共和國', '蒙特塞拉特島',
                '摩洛哥', '莫桑比克', '緬甸', '納米比亞', '尼泊爾', '荷蘭', '荷屬安的列斯群島', '新喀裡多尼亞',
                '新西蘭', '尼加拉瓜', '尼日爾', '尼日利亞', '挪威', '阿曼', '巴基斯坦', '帕勞', '巴拿馬', '巴布亞新幾內亞',
                '巴拉圭', '秘魯', '菲律賓', '波蘭', '葡萄牙', '波多黎各', '巴勒斯坦',
                '卡塔爾', '留尼旺', '羅馬尼亞', '俄羅斯聯邦', '盧旺達', '聖基茨和尼維斯', '聖盧西亞島', '聖文森特和格林納丁斯',
                '薩摩亞群島', '聖馬力諾', '沙特阿拉伯', '塞內加爾', '塞爾維亞', '塞舌爾', '塞拉利昂', '新加坡',
                '斯洛伐克', '斯洛文尼亞', '所羅門群島', '索馬里', '南非', '南蘇丹', '西班牙', '斯里蘭卡',
                '蘇丹', '蘇里南', '斯威士蘭', '瑞典', '瑞士', '阿拉伯敘利亞共和國', '中國台灣', '塔吉克斯坦', '坦桑尼亞', '泰國',
                '東帝汶', '多哥', '湯加', '特立尼達和多巴哥', '突尼斯', '土耳其', '土庫曼斯坦', '特克斯和凱科斯群島',
                '烏干達', '烏克蘭', '阿拉伯聯合酋長國', '英國', '美國', '烏拉圭',
                '烏茲別克斯坦', '瓦努阿圖', '委內瑞拉', '越南', '英屬維爾京群島', '也門',
                '贊比亞', '津巴布韋'
            ],
            countryEnList: ['Afghanistan', 'Albania', 'Algeria', 'American Samoa',
                'Andorra', 'Angola', 'Anguilla', 'Antigua and Barbuda', 'Argentina',
                'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan',
                'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus',
                'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia',
                'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei Darussalam',
                'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada',
                'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad',
                'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Congo The Democratic Republic',
                'Cook Islands', 'Costa Rica', 'Cote D"ivoire', 'Croatia', 'Cuba', 'Cyprus',
                'Czech Republic',
                'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Dubai',
                'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea',
                'Estonia', 'Ethiopia', 'Falkland Islands (Malvinas)', 'Faroe Islands',
                'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'Gabon', 'Gambia',
                'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe',
                'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong',
                'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran Islamic Republic', 'Iraq',
                'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan',
                'Kenya', "Korea Democratic People's Republic", 'Korea Republic', 'Kosovo', 'Kuwait', 'Kyrgyzstan',
                "Lao People's Democratic Republic", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libyan Arab Jamahiriya',
                'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia',
                'Maldives', 'Mali', 'Malta', 'Martinique', 'Mauritania', 'Mauritius', 'Mexico',
                'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia',
                'Nepal', 'Netherlands', 'Netherlands Antilles', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger',
                'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay',
                'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Palestine',
                'Qatar', 'Reunion', 'Romania',
                'Russian Federation', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines',
                'Samoa', 'San Marino', 'Saudi Arabia', 'Senegal', 'Serbia',
                'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands',
                'Somalia', 'South Africa', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan',
                'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Taiwan',
                'Tajikistan', 'Tanzania United Republic', 'Thailand', 'Timor-Leste', 'Togo',
                'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands',
                'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
                'Uruguay', 'Uzbekistan',
                'Vanuatu', 'Venezuela', 'Viet Nam', 'Virgin Islands British', 'Yemen',
                'Zambia', 'Zimbabwe'
            ]
        }
    },
    mounted() {
        this.countriesFind = this.countries
        this.isInit && this.getData()
    },
    watch: {
        val(newVal) {
            this.onSearch(newVal)
        }
    },
    methods: {
        //自定义打开方法
        open() {
            this.isShow = true
        },
        getData() {
            this.$emit('getName', 'United States', 'us', 1);
        },
        //选择国家
        selectItem(item, key) {
            console.log(item)
            this.selectIndex = item.code;
            this.$emit('getName', item.name, item.code, item.dialCode, key)
            this.isShow = false
        },
        //搜索国家
        onSearch(val) {
            if (!val) {
                this.countriesFind = this.countries
                return
            }
            this.countriesFind = {}

            Object.keys(this.countries).forEach((key) => {
                if (this.countries[key].name?.toLowerCase().indexOf(val?.toLowerCase()) > -1 || this.countries[key].dialCode.toString().indexOf(val) > -1) {
                    this.countriesFind[key] = this.countries[key]
                }
            })
        },
        //清空搜索
        onClear() {
            this.getData()
        }
    }
}
</script>
<style lang="scss" scoped>
@import "intl.css";

.nationList .van-action-sheet {
    height: 80%;
}

.nation-item {
    box-sizing: border-box;
    width: 100%;
    padding: 0 12px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;

    >.img {
        width: 20px;
        height: 12px;
    }

    >.name {
        flex: 1;
        margin: 0 10px;
    }
}
</style>
