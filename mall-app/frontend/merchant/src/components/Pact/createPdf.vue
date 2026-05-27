<template>
  <div class="create-pdf">
    <div class="pdf" ref="pdfView">
      <iframe v-if="show" :src="url" width="100%" height="100%" frameborder="0"></iframe>
    </div>
    <!--    <div class="close" @click="closePdf">-->
    <!--      <i class="el-icon-close" style="font-size: 36px;"></i>-->
    <!--    </div>-->
  </div>
</template>

<script>  import pdf from 'vue-pdf'
import {mapGetters} from "vuex";
import defaultSettings from "@/settings";

export default {
  name: 'Home',
  components: {
    pdf
  },
  data() {
    return {
      url: "/promote/#/pact",
      show: false,
    }
  },
  computed: {
    ...mapGetters(['userInfo']),

  },
  mounted() {
    //如果是开发环境
    if (process.env.NODE_ENV === 'development') {
      this.url = 'https://thsjbvh.site/promote/#/pact'
    }
    this.url += this.computedUrl()
    window.closePopup = () => {
      this.closePdf()
    }
    this.$nextTick(() => {
      this.show = true
    })
  },
  methods: {
    closePdf() {
      this.$emit('closePdf')
    },
    computedUrl() {
      const lang = this.$store.getters.lang;
      let token = localStorage.getItem('token')
      const queryParams = new URLSearchParams({
        token,
        lang,
        name: defaultSettings.projectTitle,
      });
      return `/?${queryParams.toString()}`;
    },
  }
}
</script>
<style lang="scss">
//当前组件设置成全屏弹窗
.create-pdf {
  width: 100%;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000000;
  overflow: hidden;

  &::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .pdf {
    width: 100%;
    height: 100%;
    position: relative;
    z-index: 1000001;
    top: 0;
    left: 0;
    overflow-y: auto;
    padding: 0;
    display: flex;
    justify-content: center;
  }

  .close {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 50px;
    height: 50px;
    cursor: pointer;
    z-index: 1000002;
    background-color: rgba(0, 0, 0, 0.3);
    color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;

    &:hover {
      background-color: rgba(0, 0, 0, 0.5);
    }
  }
}

</style>
