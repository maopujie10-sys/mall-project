<script>
export default {

    props: ['text'],

    render() {
        return <span class='ten-pix'>
            {this.text}
        </span>
    },
}
</script>


<style lang="scss" scoped>
.ten-pix {
    display: inline-block;
    font-size: 20px;
    transform: scale(.5);
    white-space: nowrap;
    // margin-left: -30px;
}
</style>
