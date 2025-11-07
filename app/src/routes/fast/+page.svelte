<script lang="ts">
    import ioClient from 'socket.io-client';
    import {onMount} from 'svelte';

    // This page is identical to the "slow" version, except this one doesn't use svelvet
    // For a commented version, see the other page

    onMount(() => {
        start(prompt("from")!,prompt("to")!)
    });

    const sio = ioClient('http://localhost:5000')

    sio.on("searching",(data) => {
        let explored = data.path as string[]

        currpath = explored.join(" --> ")
    })

    function start(start:string,end:string) {
        sio.emit("start",{from:start,to:end,sleeptime:0})
    }


    let currpath = $state()
</script>

<h2>{currpath}</h2>