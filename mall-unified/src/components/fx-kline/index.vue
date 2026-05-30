<template>
    <div id="kline" :style="{ height: `${props.height || defaultH}px` }" v-if="defaultH">
    </div>
</template>

<script setup>
import { init, dispose } from 'klinecharts'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue-demi'
import config from './config'
import fakeData from './fake-data'
import { _getKline } from '@/service/charts.api'
import { WS_URL } from '@/config'
import { useQuotesStore } from '@/store/quotes.store'

const quotesStore = useQuotesStore()

let chart = null

const paneId = ref('')

const data = ref(fakeData)

const defaultH = ref(0)

const socket = ref(null)

const emits = defineEmits(['data'])

onMounted(() => {
    defaultH.value = window.innerHeight - 94
    nextTick(async () => {
        await initData()
        startQuoteScoket()
    })
})

const props = defineProps({
    symbol: {
        type: String
    },
    height: {
        type: String
    },
    chartType: {
        type: String,
        default: 'candle_solid'
    }
})

const startQuoteScoket = () => {
    closeSocket()
    socket.value = new WebSocket(`${WS_URL}/1/${props.symbol}`)
    socket.value.onmessage = (evt) => {
        const { data } = evt
        const { code, data: _data } = JSON.parse(data)
        if (code / 1 === 0) {
            emits('data', _data[0])
            updateCharts(_data[0])
        }
    }
}

onBeforeUnmount(() => {
    closeSocket()
})

const closeSocket = () => {
    socket.value && socket.value.close()
    socket.value = null
}


const updateCharts = (nowData) => {
    const dataList = chart.getDataList()
    const lastData = dataList[dataList.length - 1]
    // const nowData = this.updateData
    // const timeValue = this.timeValue
    // nowData.timestamp = nowData.ts
    const newData = {
        close: nowData.close / 1,
        current_time: lastData.current_time,
        high: lastData.high > nowData.close / 1 ? lastData.high : (nowData.close / 1),
        // high: lastData.high,
        line: quotesStore.stage, // timeValue.id,
        low: lastData.low < nowData.close / 1 ? lastData.low : (nowData.close / 1),
        // low: lastData.low,
        open: lastData.open,
        symbol: lastData.symbol,
        // timestamp: lastData.timestamp, //
        // timestamp: nowData.ts || nowData.timestamp, //
        timestamp: (nowData.timestamp - lastData.timestamp) < quotesStore.seconds ? lastData.timestamp : (lastData.timestamp + quotesStore.seconds),
        // volume: lastData.volume / 1,
        volume: nowData.volume / 1
    }
    nextTick(() => {
        chart.setStyleOptions({
            candle: {
                type: props.chartType
            }
        })
        chart.updateData(newData)
    })
}

const initData = async () => {
    // this.timeValue = this.timeList[0]
    chart = init('kline', config);
    chart.setOffsetRightSpace(25)
    chart.setDataSpace(10)
    chart.setPriceVolumePrecision(4, 2)
    if (props.type === 'candle_solid') {
        chart.createTechnicalIndicator('MA', false, { id: 'candle_pane' });
        paneId.value = chart.createTechnicalIndicator('VOL');
    }

    // this.fetchData()
    chart.setStyleOptions({
        candle: {
            type: props.chartType
        }
    })

    data.value = await _getKline(props.symbol, quotesStore.stage)
    // console.log(data.value)

    nextTick(() => {
        chart.applyNewData(data.value);
    })
}

</script>
