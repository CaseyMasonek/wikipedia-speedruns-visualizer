<script lang="ts">
    import ioClient from 'socket.io-client';
    import { Node, Svelvet } from 'svelvet';
    import {onMount,onDestroy} from 'svelte';

    // Initialize window height
    let windowHeight: number = $state(0);

    onMount(() => {
        // Run once page is mounted

        // Get window height
        windowHeight = window.innerHeight;

        const handleResize = () => {
            windowHeight = window.innerHeight;
        };
        window.addEventListener('resize', handleResize);

        onDestroy(() => {
            window.removeEventListener('resize', handleResize);
        });

        // Send message to server
        start(prompt("from")!,prompt("to")!)
    });

    const sio = ioClient('http://localhost:5000') // Connect to server

    const graph : Record<string,string[]> = $state({}) // Initialize graph

    sio.on("searching",(data) => {
        // When message from client is recieved

        let explored = data.path as string[] // Get the path

        currpath = explored.join(" --> ") // for text representation

        if (!explored) return;

        const from = explored.at(-2)
        const to = explored.at(-1)

        if (from !== undefined && to !== undefined) {
            // Update graph representation on the client side
            if (!!graph[from]) {
                graph[from].push(to)
            } else {
                graph[from] = [to]
            }
        }
    })

    function start(start:string,end:string) {
        // Send a message to the server
        sio.emit("start",{from:start,to:end,sleeptime:0.2})
    }

    const rand = () => Math.random() * (10000); // For random position

    let currpath = $state() // State for text representation of the current path
</script>

<h2>{currpath}</h2>

<Svelvet height={windowHeight - 20}>
    <!-- Render nodes w/ svelvet -->
    {#each Object.entries(graph) as [from,to]}
        <Node label={from} id={from} position={{ x: rand(), y: rand() }} />
        {#each to as end}
            <Node label={end} id={end} connections={[from]} position={{ x: rand(), y: rand() }} />
        {/each}
    {/each}
</Svelvet>