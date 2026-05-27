<template>
  <div class="lang-content">
    <el-dropdown trigger="click">
      <span class="lang-select">
        <img
          :src="langIcon[currentLang]"
          alt=""
          style="width: 18px; border-radius: 50%"
        />
        <i class="el-icon-caret-bottom"></i>
      </span>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.en)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.en]"
              :alt="ES_LANGUAGE_MAP.en"
              style="width: 18px"
            />
            <span>English</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.de)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.de]"
              :alt="ES_LANGUAGE_MAP.de"
              style="width: 18px"
            />
            <span>Deutsch</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.fr)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.fr]"
              :alt="ES_LANGUAGE_MAP.fr"
              style="width: 18px"
            />
            <span>français</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ru)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ru]"
              :alt="ES_LANGUAGE_MAP.ru"
              style="width: 18px; border-radius: 50%"
            />
            <span>Русский</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.es)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.es]"
              :alt="ES_LANGUAGE_MAP.es"
              style="width: 18px"
            />
            <span>Español</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.pt)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.pt]"
              :alt="ES_LANGUAGE_MAP.pt"
              style="width: 18px"
            />
            <span>Português</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.it)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.it]"
              :alt="ES_LANGUAGE_MAP.it"
              style="width: 18px"
            />
            <span>Italiano</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ms)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ms]"
              :alt="ES_LANGUAGE_MAP.ms"
              style="width: 18px"
            />
            <span>Melayu</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.af)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.af]"
              :alt="ES_LANGUAGE_MAP.af"
              style="width: 18px"
            />
            <span>Afrikaans</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.el)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.el]"
              :alt="ES_LANGUAGE_MAP.el"
              style="width: 18px"
            />
            <span>Ελληνικά</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item v-if="itemname !== 'Mbuy'">
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.zhTW)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.zhTW]"
              :alt="ES_LANGUAGE_MAP.zhTW"
              style="width: 18px"
            />
            <span>中文繁體</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item v-if="itemname !== 'Mbuy'">
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.zhCN)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.zhCN]"
              :alt="ES_LANGUAGE_MAP.zhCN"
              style="width: 18px"
            />
            <span>中文简体</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.tr)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.tr]"
              :alt="ES_LANGUAGE_MAP.tr"
              style="width: 18px"
            />
            <span>Türkçe</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ja)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ja]"
              :alt="ES_LANGUAGE_MAP.ja"
              style="width: 18px"
            />
            <span>日本語</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ko)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ko]"
              :alt="ES_LANGUAGE_MAP.ko"
              style="width: 18px"
            />
            <span>한국어</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.th)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.th]"
              :alt="ES_LANGUAGE_MAP.th"
              style="width: 18px"
            />
            <span>ภาษาไทย</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ph)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ph]"
              :alt="ES_LANGUAGE_MAP.ph"
              style="width: 18px"
            />
            <span>Filipino</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.ar)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.ar]"
              :alt="ES_LANGUAGE_MAP.ar"
              style="width: 18px"
            />
            <span>العربية</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.vi)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.vi]"
              :alt="ES_LANGUAGE_MAP.vi"
              style="width: 18px"
            />
            <span>Tiếng Việt</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.hi)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.hi]"
              :alt="ES_LANGUAGE_MAP.hi"
              style="width: 18px"
            />
            <span>हिन्दी</span>
          </div>
        </el-dropdown-item>
        <el-dropdown-item>
          <div class="lang-item" @click="changeLang(ES_LANGUAGE_MAP.id)">
            <img
              :src="langIcon[ES_LANGUAGE_MAP.id]"
              :alt="ES_LANGUAGE_MAP.id"
              style="width: 18px"
            />
            <span>Bahasa Indonesia</span>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import zhIcon from "@/assets/image/cn.png";
import enIcon from "@/assets/image/en.png";
import twIcon from "@/assets/image/tw.png";
import jaIcon from "@/assets/image/lang-icon/ja.png";
import deIcon from "@/assets/image/lang-icon/de.png";
import msIcon from "@/assets/image/lang-icon/ms.png";
import afIcon from "@/assets/image/lang-icon/af.png";
import thIcon from "@/assets/image/lang-icon/th.png";
import elIcon from "@/assets/image/lang-icon/el.png";
import ptIcon from "@/assets/image/lang-icon/pt.png";
import esIcon from "@/assets/image/lang-icon/es.png";
import frIcon from "@/assets/image/lang-icon/fr.png";
import ruIcon from "@/assets/image/lang-icon/ru.png";
import itIcon from "@/assets/image/lang-icon/it.png";
import trIcon from "@/assets/image/lang-icon/tr.png";
import koIcon from "@/assets/image/lang-icon/ko.png";
import phIcon from "@/assets/image/lang-icon/ph.png";
import arIcon from "@/assets/image/lang-icon/ar.png";
import idIcon from "@/assets/image/lang-icon/id.png";
import viIcon from "@/assets/image/lang-icon/vi.png";
import hiIcon from "@/assets/image/lang-icon/hi.png";
import { ES_LANGUAGE_MAP } from "@/common";
import { setLocal } from "@/lang/i18n";
export default {
  name: "EsLang",
  data() {
    return {
      itemname: process.env.VUE_APP_ITEM_NAME,
      langIcon: {
        [ES_LANGUAGE_MAP.zhCN]: zhIcon,
        [ES_LANGUAGE_MAP.en]: enIcon,
        [ES_LANGUAGE_MAP.zhTW]: twIcon,
        [ES_LANGUAGE_MAP.ja]: jaIcon,
        [ES_LANGUAGE_MAP.de]: deIcon,
        [ES_LANGUAGE_MAP.ms]: msIcon,
        [ES_LANGUAGE_MAP.af]: afIcon,
        [ES_LANGUAGE_MAP.th]: thIcon,
        [ES_LANGUAGE_MAP.el]: elIcon,
        [ES_LANGUAGE_MAP.pt]: ptIcon,
        [ES_LANGUAGE_MAP.es]: esIcon,
        [ES_LANGUAGE_MAP.fr]: frIcon,
        [ES_LANGUAGE_MAP.ru]: ruIcon,
        [ES_LANGUAGE_MAP.it]: itIcon,
        [ES_LANGUAGE_MAP.tr]: trIcon,
        [ES_LANGUAGE_MAP.ko]: koIcon,
        [ES_LANGUAGE_MAP.ph]: phIcon,
        [ES_LANGUAGE_MAP.ar]: arIcon,
        [ES_LANGUAGE_MAP.id]: idIcon,
        [ES_LANGUAGE_MAP.vi]: viIcon,
        [ES_LANGUAGE_MAP.hi]: hiIcon, 
      },
      ES_LANGUAGE_MAP,
    };
  },
  computed: {
    ...mapGetters(["currentLang"]),
  },
  methods: {
    changeLang(lang) {
      setLocal(lang, () => {
        if (this.$route.query.lang) {
          const query = { ...this.$route.query };
          delete query.lang;
          this.$router.replace({ query });
        }
        localStorage.setItem("scroll", 0);
        window.location.reload();
      });
    },
  },
};
</script>

<style lang="scss">
html[dir="rtl"]{
   .el-dropdown {
    margin-right: 26px !important;
    margin-left: 0 !important;
   }
   .lang-select {
    i{
      margin-right: 5px;
      margin-left: 0;
    }
   }
   .lang-item span {
    margin-right: 8px;
}
}
.lang-content {
  .el-dropdown {
    margin-left: 26px;
    margin-top: 3px;
  }

  .lang-select {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    cursor: pointer;

    i {
      margin-left: 5px;
    }
  }
}
.el-dropdown-menu {
  height: 300px !important;
  overflow-y: auto !important;
}
</style>
