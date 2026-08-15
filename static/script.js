// ============================================================
// ALEPHZERO WEB CLIENT v3.1
// Text Chat + Vision Upload + Backend Health
// ============================================================

"use strict";


// ============================================================
// ENDPOINTS
// ============================================================

const CHAT_ENDPOINT = "/chat";
const VISION_ENDPOINT = "/vision";
const HEALTH_ENDPOINT = "/health";


// ============================================================
// STATE
// ============================================================

let messageInput;
let sendButton;
let messagesContainer;
let typingIndicator;
let newChatButton;

let statusText;
let headerStatus;

let imageButton;
let imageInput;
let imagePreview;
let previewImage;
let removeImageButton;

let selectedImage = null;
let isSending = false;


// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    initializeApp
);


function initializeApp() {

    messageInput =
        document.getElementById("messageInput");

    sendButton =
        document.getElementById("sendButton");

    messagesContainer =
        document.getElementById("messages");

    typingIndicator =
        document.getElementById("typingIndicator");

    newChatButton =
        document.getElementById("newChatButton");

    statusText =
        document.getElementById("statusText");

    headerStatus =
        document.getElementById("headerStatus");

    imageButton =
        document.getElementById("imageButton");

    imageInput =
        document.getElementById("imageInput");

    imagePreview =
        document.getElementById("imagePreview");

    previewImage =
        document.getElementById("previewImage");

    removeImageButton =
        document.getElementById("removeImage");


    if (
        !messageInput ||
        !sendButton ||
        !messagesContainer
    ) {

        console.error(
            "ALEPHZERO: Required UI elements are missing."
        );

        return;
    }


    setupEventListeners();

    autoResize();

    checkBackend();

    messageInput.focus();
}


// ============================================================
// EVENT LISTENERS
// ============================================================

function setupEventListeners() {


    // --------------------------------------------------------
    // SEND BUTTON
    // --------------------------------------------------------

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    // --------------------------------------------------------
    // KEYBOARD
    // --------------------------------------------------------

    messageInput.addEventListener(
        "keydown",
        handleKeyboardInput
    );


    messageInput.addEventListener(
        "input",
        autoResize
    );


    // --------------------------------------------------------
    // NEW CHAT
    // --------------------------------------------------------

    if (newChatButton) {

        newChatButton.addEventListener(
            "click",
            startNewChat
        );
    }


    // --------------------------------------------------------
    // IMAGE BUTTON
    // --------------------------------------------------------

    if (imageButton && imageInput) {

        imageButton.addEventListener(
            "click",
            function () {

                imageInput.click();

            }
        );
    }


    // --------------------------------------------------------
    // IMAGE SELECTION
    // --------------------------------------------------------

    if (imageInput) {

        imageInput.addEventListener(
            "change",
            handleImageSelection
        );
    }


    // --------------------------------------------------------
    // REMOVE IMAGE
    // --------------------------------------------------------

    if (removeImageButton) {

        removeImageButton.addEventListener(
            "click",
            removeSelectedImage
        );
    }
}


// ============================================================
// KEYBOARD INPUT
// ============================================================

function handleKeyboardInput(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.ctrlKey &&
        !event.altKey
    ) {

        event.preventDefault();

        sendMessage();
    }
}


// ============================================================
// HEALTH CHECK
// ============================================================

async function checkBackend() {

    try {

        const response = await fetch(
            HEALTH_ENDPOINT,
            {
                method: "GET",
                cache: "no-store"
            }
        );


        if (!response.ok) {

            throw new Error(
                `Backend returned HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        if (data.status === "online") {

            setOnlineStatus();

        } else {

            setOfflineStatus();
        }


    } catch (error) {

        console.error(
            "ALEPHZERO health check failed:",
            error
        );

        setOfflineStatus();
    }
}


// ============================================================
// STATUS
// ============================================================

function setOnlineStatus() {

    if (statusText) {

        statusText.textContent =
            "Backend online";
    }


    if (headerStatus) {

        headerStatus.textContent =
            "Online";
    }
}


function setOfflineStatus() {

    if (statusText) {

        statusText.textContent =
            "Backend offline";
    }


    if (headerStatus) {

        headerStatus.textContent =
            "Offline";
    }
}


// ============================================================
// IMAGE SELECTION
// ============================================================

function handleImageSelection(event) {

    const file =
        event.target.files &&
        event.target.files[0];


    if (!file) {

        return;
    }


    // --------------------------------------------------------
    // Validate file type
    // --------------------------------------------------------

    if (!file.type.startsWith("image/")) {

        alert(
            "Please select a valid image file."
        );

        imageInput.value = "";

        return;
    }


    // --------------------------------------------------------
    // Validate file size
    // --------------------------------------------------------

    const maxSize =
        10 * 1024 * 1024;


    if (file.size > maxSize) {

        alert(
            "Image is too large. Maximum size is 10 MB."
        );

        imageInput.value = "";

        return;
    }


    selectedImage = file;


    // --------------------------------------------------------
    // Create preview
    // --------------------------------------------------------

    const reader =
        new FileReader();


    reader.onload = function (readerEvent) {

        if (previewImage) {

            previewImage.src =
                readerEvent.target.result;
        }


        if (imagePreview) {

            imagePreview.classList.remove(
                "hidden"
            );
        }
    };


    reader.readAsDataURL(file);
}


// ============================================================
// REMOVE IMAGE
// ============================================================

function removeSelectedImage() {

    selectedImage = null;


    if (imageInput) {

        imageInput.value = "";
    }


    if (previewImage) {

        previewImage.src = "";
    }


    if (imagePreview) {

        imagePreview.classList.add(
            "hidden"
        );
    }
}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    if (isSending) {

        return;
    }


    const message =
        messageInput.value.trim();


    // --------------------------------------------------------
    // Nothing to send
    // --------------------------------------------------------

    if (
        !message &&
        !selectedImage
    ) {

        return;
    }


    isSending = true;


    messageInput.disabled = true;
    sendButton.disabled = true;


    try {


        // ====================================================
        // VISION REQUEST
        // ====================================================

        if (selectedImage) {

            await sendVisionRequest(
                message
            );

        }


        // ====================================================
        // NORMAL CHAT REQUEST
        // ====================================================

        else {

            await sendChatRequest(
                message
            );
        }


    } catch (error) {

        console.error(
            "ALEPHZERO request error:",
            error
        );


        hideTyping();


        addMessage(
            "I couldn't communicate with the ALEPHZERO backend.\n\n" +
            "Error: " +
            error.message,
            "assistant"
        );


        setOfflineStatus();


    } finally {

        isSending = false;

        messageInput.disabled = false;

        sendButton.disabled = false;

        messageInput.focus();
    }
}


// ============================================================
// NORMAL CHAT REQUEST
// ============================================================

async function sendChatRequest(message) {


    // --------------------------------------------------------
    // Display user message
    // --------------------------------------------------------

    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    autoResize();

    showTyping();


    // --------------------------------------------------------
    // Request backend
    // --------------------------------------------------------

    const response =
        await fetch(
            CHAT_ENDPOINT,
            {
                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        message: message
                    })
            }
        );


    const data =
        await parseJsonResponse(
            response
        );


    hideTyping();


    if (
        !data ||
        typeof data.response !== "string"
    ) {

        throw new Error(
            "ALEPHZERO returned an empty response."
        );
    }


    // --------------------------------------------------------
    // Display response
    // --------------------------------------------------------

    addMessage(
        data.response,
        "assistant",
        data.tool_used || null
    );


    setOnlineStatus();
}


// ============================================================
// VISION REQUEST
// ============================================================

async function sendVisionRequest(message) {


    // --------------------------------------------------------
    // Display image + question in chat
    // --------------------------------------------------------

    addImageMessage(
        selectedImage,
        message
    );


    showTyping();


    // --------------------------------------------------------
    // Prepare multipart form
    // --------------------------------------------------------

    const formData =
        new FormData();


    formData.append(
        "image",
        selectedImage
    );


    formData.append(
        "message",
        message || "Analyze this image."
    );


    // --------------------------------------------------------
    // Send to /vision
    // --------------------------------------------------------

    const response =
        await fetch(
            VISION_ENDPOINT,
            {
                method: "POST",

                body: formData
            }
        );


    const data =
        await parseJsonResponse(
            response
        );


    hideTyping();


    if (
        !data ||
        typeof data.response !== "string"
    ) {

        throw new Error(
            "ALEPHZERO vision service returned an empty response."
        );
    }


    // --------------------------------------------------------
    // Display vision response
    // --------------------------------------------------------

    addMessage(
        data.response,
        "assistant",
        data.tool_used || "vision"
    );


    setOnlineStatus();


    // --------------------------------------------------------
    // Clear image
    // --------------------------------------------------------

    removeSelectedImage();
}


// ============================================================
// PARSE SERVER RESPONSE
// ============================================================

async function parseJsonResponse(response) {

    let data;


    try {

        data =
            await response.json();

    } catch (error) {

        throw new Error(
            "ALEPHZERO returned an invalid server response."
        );
    }


    if (!response.ok) {

        throw new Error(
            data.detail ||
            `Server returned HTTP ${response.status}`
        );
    }


    return data;
}


// ============================================================
// ADD TEXT MESSAGE
// ============================================================

function addMessage(
    text,
    sender,
    toolUsed = null
) {

    const message =
        document.createElement("div");


    message.className =
        sender === "user"
            ? "message user-message"
            : "message assistant-message";


    const avatar =
        document.createElement("div");


    avatar.className =
        "avatar";


    avatar.textContent =
        sender === "user"
            ? "U"
            : "A";


    const content =
        document.createElement("div");


    content.className =
        "message-content";


    const name =
        document.createElement("div");


    name.className =
        "message-name";


    name.textContent =
        sender === "user"
            ? "YOU"
            : "ALEPHZERO";


    const messageText =
        document.createElement("div");


    messageText.className =
        "message-text";


    /*
     * textContent is deliberately used instead
     * of innerHTML for model responses.
     */

    messageText.textContent =
        text;


    content.appendChild(
        name
    );


    content.appendChild(
        messageText
    );


    // --------------------------------------------------------
    // Tool indicator
    // --------------------------------------------------------

    if (
        sender === "assistant" &&
        toolUsed
    ) {

        const toolIndicator =
            document.createElement("div");


        toolIndicator.className =
            "tool-used";


        toolIndicator.textContent =
            "Tool used: " +
            formatToolName(toolUsed);


        content.appendChild(
            toolIndicator
        );
    }


    message.appendChild(
        avatar
    );


    message.appendChild(
        content
    );


    messagesContainer.appendChild(
        message
    );


    scrollToBottom();
}


// ============================================================
// ADD IMAGE MESSAGE
// ============================================================

function addImageMessage(
    file,
    message
) {

    const container =
        document.createElement("div");


    container.className =
        "message user-message";


    const avatar =
        document.createElement("div");


    avatar.className =
        "avatar";


    avatar.textContent =
        "U";


    const content =
        document.createElement("div");


    content.className =
        "message-content";


    const name =
        document.createElement("div");


    name.className =
        "message-name";


    name.textContent =
        "YOU";


    content.appendChild(
        name
    );


    // --------------------------------------------------------
    // Image
    // --------------------------------------------------------

    const image =
        document.createElement("img");


    image.className =
        "chat-image";


    image.alt =
        file.name;


    image.src =
        URL.createObjectURL(file);


    image.style.maxWidth =
        "320px";


    image.style.maxHeight =
        "320px";


    image.style.borderRadius =
        "12px";


    image.style.display =
        "block";


    image.style.marginBottom =
        "10px";


    content.appendChild(
        image
    );


    // --------------------------------------------------------
    // Question
    // --------------------------------------------------------

    if (message) {

        const messageText =
            document.createElement("div");


        messageText.className =
            "message-text";


        messageText.textContent =
            message;


        content.appendChild(
            messageText
        );
    }


    container.appendChild(
        avatar
    );


    container.appendChild(
        content
    );


    messagesContainer.appendChild(
        container
    );


    scrollToBottom();
}


// ============================================================
// TOOL NAME
// ============================================================

function formatToolName(toolName) {

    const names = {

        "time_information":
            "Current Time",

        "system_information":
            "System Information",

        "calculator":
            "Calculator",

        "vision":
            "Vision / Gemma3"
    };


    return (
        names[toolName] ||
        toolName
    );
}


// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {

    if (!typingIndicator) {

        return;
    }


    typingIndicator.classList.remove(
        "hidden"
    );


    scrollToBottom();
}


function hideTyping() {

    if (!typingIndicator) {

        return;
    }


    typingIndicator.classList.add(
        "hidden"
    );
}


// ============================================================
// SCROLL
// ============================================================

function scrollToBottom() {

    requestAnimationFrame(
        function () {

            messagesContainer.scrollTop =
                messagesContainer.scrollHeight;

        }
    );
}


// ============================================================
// TEXTAREA AUTO RESIZE
// ============================================================

function autoResize() {

    if (!messageInput) {

        return;
    }


    messageInput.style.height =
        "auto";


    const height =
        Math.min(
            messageInput.scrollHeight,
            150
        );


    messageInput.style.height =
        height + "px";
}


// ============================================================
// NEW CHAT
// ============================================================

function startNewChat() {

    const confirmed =
        confirm(
            "Start a new conversation?"
        );


    if (!confirmed) {

        return;
    }


    messagesContainer.innerHTML =
        "";


    addMessage(
        "New conversation started.\n\nHow can I help you?",
        "assistant"
    );


    messageInput.value =
        "";


    autoResize();


    removeSelectedImage();


    messageInput.focus();
}


// ============================================================
// GLOBAL ERROR HANDLING
// ============================================================

window.addEventListener(
    "error",
    function (event) {

        console.error(
            "ALEPHZERO JavaScript error:",
            event.error ||
            event.message
        );
    }
);


window.addEventListener(
    "unhandledrejection",
    function (event) {

        console.error(
            "ALEPHZERO unhandled promise rejection:",
            event.reason
        );
    }
);