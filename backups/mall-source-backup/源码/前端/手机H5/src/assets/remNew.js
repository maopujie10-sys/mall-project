const baseSize = 16
function setRem() {
    var chicun = document.documentElement.clientWidth
    // console.log(chicun)
    if (chicun>570){
        chicun = 570
    }
    // console.log(chicun)
    const scale = chicun / 375
    document.documentElement.style.fontSize = baseSize * scale + 'px'
}
setRem()
window.onresize = function () {
    setRem()
}
