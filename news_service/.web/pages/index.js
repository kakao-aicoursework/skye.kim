import { Fragment, useEffect, useRef, useState } from "react"
import { useRouter } from "next/router"
import { connect, E, getRefValue, isTrue, preventDefault, processEvent, refs, set_val, uploadFiles } from "/utils/state"
import "focus-visible/dist/focus-visible"
import "gridjs/dist/theme/mermaid.css"
import { Box, Button, Center, Heading, HStack, Input, Spinner, Text, useColorMode, VStack } from "@chakra-ui/react"
import { Grid as DataTableGrid } from "gridjs-react"
import NextHead from "next/head"


export default function Component() {
  const [state, setState] = useState({"columns": ["title", "url", "summary"], "data": [], "is_hydrated": false, "is_working": false, "topic": "", "events": [{"name": "state.hydrate"}], "files": []})
  const [result, setResult] = useState({"state": null, "events": [], "final": true, "processing": false})
  const [notConnected, setNotConnected] = useState(false)
  const router = useRouter()
  const socket = useRef(null)
  const { isReady } = router
  const { colorMode, toggleColorMode } = useColorMode()
  const focusRef = useRef();
  
  // Function to add new events to the event queue.
  const Event = (events, _e) => {
      preventDefault(_e);
      setState(state => ({
        ...state,
        events: [...state.events, ...events],
      }))
  }

  // Function to add new files to be uploaded.
  const File = files => setState(state => ({
    ...state,
    files,
  }))

  // Main event loop.
  useEffect(()=> {
    // Skip if the router is not ready.
    if (!isReady) {
      return;
    }

    // Initialize the websocket connection.
    if (!socket.current) {
      connect(socket, state, setState, result, setResult, router, ['websocket', 'polling'], setNotConnected)
    }

    // If we are not processing an event, process the next event.
    if (!result.processing) {
      processEvent(state, setState, result, setResult, router, socket.current)
    }

    // If there is a new result, update the state.
    if (result.state != null) {
      // Apply the new result to the state and the new events to the queue.
      setState(state => ({
        ...result.state,
        events: [...state.events, ...result.events],
      }))

      // Reset the result.
      setResult(result => ({
        state: null,
        events: [],
        final: true,
        processing: !result.final,
      }))

      // Process the next event.
      processEvent(state, setState, result, setResult, router, socket.current)
    }
  })

  // Set focus to the specified element.
  useEffect(() => {
    if (focusRef.current) {
      focusRef.current.focus();
    }
  })

  // Route after the initial page hydration.
  useEffect(() => {
    const change_complete = () => Event([E('state.hydrate', {})])
    router.events.on('routeChangeComplete', change_complete)
    return () => {
      router.events.off('routeChangeComplete', change_complete)
    }
  }, [router])


  return (
  <Fragment><Fragment>
  <Center sx={{"paddingTop": "10%"}}>
  <VStack sx={{"width": "80%", "fontSize": "1em"}}>
  <Heading sx={{"fontSize": "2em"}}>
  {`뉴스 크롤링 & 요약 서비스`}
</Heading>
  <Input onBlur={_e => Event([E("state.set_topic", {value:_e.target.value})], _e)} placeholder="topic" type="text"/>
  <HStack>
  <Button onClick={_e => Event([E("state.handle_submit", {})], _e)}>
  {`시작`}
</Button>
  <Button onClick={_e => Event([E("state.export", {})], _e)}>
  {`excel로 export`}
</Button>
  <Button onClick={_e => Event([E("state.delete_all", {})], _e)}>
  {`모두 삭제`}
</Button>
</HStack>
  <Fragment>
  {isTrue(state.is_working) ? (
  <Fragment>
  <Spinner size="xl" speed="1.5s" sx={{"color": "lightgreen"}} thickness={5}/>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <DataTableGrid columns={state.columns} data={state.data} pagination={true} search={true} sort={false}/>
</VStack>
</Center>
  <NextHead>
  <title>
  {`Pynecone App`}
</title>
  <meta content="A Pynecone app." name="description"/>
  <meta content="favicon.ico" property="og:image"/>
</NextHead>
</Fragment>
    </Fragment>
  )
}
