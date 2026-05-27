<template>
  <div class="KIP">
    <iframe :src="nq" scrolling="auto" frameborder="0" class="nq-ys"></iframe>
  </div>
</template>
<script>
import {shouyexinxi_post} from "@/API/user";

export default {
  data(){
    return{
      nq:''
    }
  },
  components:{
  },
  created() {
    this.shouyexinxi()
  },
  methods:{
    shouyexinxi() {
      console.log(this.$i18n.locale)
      shouyexinxi_post({}).then(res => {
        console.log(res)
        this.nq = res.aboutus
      })
      // this.nq = 'https://kip.xy888org.com/'
    },
  }
}
</script>
<style lang="scss" scoped>
.KIP{
  width: 100%;
  height: 100%;
  .nq-ys{
    width: 100%;
    height: 100%;
  }

}
</style>
<style>
/*- scrollbar -*/
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-thumb{
  background-color: #999;
  -webkit-border-radius: 5px;
  border-radius: 5px;
}
::-webkit-scrollbar-thumb:vertical:hover{
  background-color: #666;
}
::-webkit-scrollbar-thumb:vertical:active{
  background-color: #333;
}
::-webkit-scrollbar-button{
  display: none;
}
::-webkit-scrollbar-track{
  background-color: #f1f1f1;
}
</style>