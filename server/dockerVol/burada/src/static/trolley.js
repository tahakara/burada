let beat = {
    count: 0, 
    success: 0, 
    fail: 0, 
    last: {
        is_success: null,
        success: { time: null }, 
        fail: { time: null },
        time: null
    }
};

let ipInfo = {ipfy: null, ipme: null};
const dust = {
    host: 'dust.tahakara.dev',
    ip: '/ip',
    beat: '/beat',
    device: '/device',
    hostUri: `https://dust.tahakara.dev`
};

let deviceInfo = null;

// Function to get the current Unix timestamp
function getUnixTime() {
    return Date.now()
}

// Function to get a cookie value by name
function getCookie(name) {
    const cookies = document.cookie.split('; ');
    for (let cookie of cookies) {
        const [key, value] = cookie.split('=');
        if (key === name) {
            return decodeURIComponent(value);
        }
    }
    return null;
}

// Set a cookie value into localStorage
function setCookieToLocalStorage(cookieName, localStorageKey) {
    const cookieValue = getCookie(cookieName);
    const storedValue = localStorage.getItem(localStorageKey);

    if (cookieValue) {
        if (storedValue !== cookieValue) {
            localStorage.setItem(localStorageKey, cookieValue);
        }
    } else {
        localStorage.removeItem(localStorageKey);
        console.warn(`"${cookieName}" is missing. Looks like someone cleaned it up!`);
    }
}

async function getIpAddress() {
    try {
        const ipfyResponse = await fetch('https://api.ipify.org?format=json');
        const ipfyData = await ipfyResponse.json();
        ipInfo.ipfy = ipfyData;
        console.log('ipfy data =>', ipfyData);
    } catch (error) {
        ipInfo.ipfy = null;
        console.error('Error fetching ipfy data', error);
    }

    try {
        const ipmeResponse = await fetch(`${dust.hostUri}${dust.ip}?t=${getUnixTime()}&r=${window.location.href}`, {
            credentials: 'include',
            referrerPolicy: 'strict-origin-when-cross-origin',
            referrer: window.location.href || document.referrer
        });
        const ipmeData = await ipmeResponse.json();
        ipInfo.ipme = ipmeData;
        console.log('ipme data =>', ipmeData);
    } catch (error) {
        ipInfo.ipme = null;
        console.error('Error fetching ipme data', error);
    }

    if (ipInfo.ipfy === null && ipInfo.ipme === null) {
        return null;
    }
    return ipInfo;
}

function heartbeat(s = 5000) {
    setInterval(async () => {
        let t = getUnixTime();
        try {
            const response = await fetch(`${dust.hostUri}${dust.beat}?t=${t}&r=${window.location.href}`, {
                credentials: 'include',
                referrerPolicy: 'strict-origin-when-cross-origin',
                referrer: window.location.href || document.referrer
            });

            if (response.ok) {
                beat.success++;
                beat.last.is_success = true;
                beat.last.success.time = t;
            } else {
                beat.fail++;
                beat.last.is_success = false;
                beat.last.fail.time = t;
            }
        } catch (error) {
            beat.fail++;
            beat.last.is_success = false;
            beat.last.fail.time = t;
            console.error('Error during heartbeat:', error);
        }
        beat.count++;
    }, s);
}

function getExtendedDeviceInfo() {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    const debugInfo = gl ? gl.getExtension("WEBGL_debug_renderer_info") : null;

    return {
        ipAddress: ipInfo,
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        languages: navigator.languages,
        screen: {
            width: screen.width,
            height: screen.height,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            colorDepth: screen.colorDepth,
            pixelRatio: window.devicePixelRatio
        },
        hardware: {
            deviceMemory: navigator.deviceMemory || null,
            cores: navigator.hardwareConcurrency || null,
            gpu: gl && debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
            webglVendor: gl && debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
        },
        network: {
            connectionType: navigator.connection?.effectiveType || null,
            downlink: navigator.connection?.downlink + " Mbps" || null,
            rtt: navigator.connection?.rtt || null,
            saveData: navigator.connection?.saveData ? true : false
        },
        browser: {
            appCodeName: navigator.appCodeName,
            appName: navigator.appName,
            appVersion: navigator.appVersion,
            product: navigator.product,
            productSub: navigator.productSub,
            vendor: navigator.vendor,
            vendorSub: navigator.vendorSub
        },
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        locale: Intl.DateTimeFormat().resolvedOptions().locale,
        touchSupport: navigator.maxTouchPoints > 0 ? true : false,
        cookiesEnabled: navigator.cookieEnabled ? true : false,
        javaEnabled: navigator.javaEnabled ? navigator.javaEnabled() ? true : false : null,
        doNotTrack: navigator.doNotTrack === "1" ? true : false,
    };
}

async function sentDeviceInfo() {
    if (!ipInfo.ipfy && !ipInfo.ipme) {
        console.warn('IP Info not available. Device info will not be sent.');
        return;
    }

    deviceInfo = getExtendedDeviceInfo();

    const data = {
        beat: beat,
        device: deviceInfo,
        r: window.location.href,
    };
    console.log('Sending Device Info => ', data);
    try {
        const response = await fetch(`${dust.hostUri}${dust.device}?r=${data.r}`, {
            method: 'POST',
            referrerPolicy: 'strict-origin-when-cross-origin',
            referrer: window.location.href || document.referrer,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });

        if (response.ok) {
            console.log('Device info sent successfully');
        } else {
            console.error('Failed to send device info');
        }
    } catch (error) {
        console.error('Error sending device info:', error);
    }
}

async function loadSequence() {
    await getIpAddress();
    setCookieToLocalStorage('dust', 'dust');
    setCookieToLocalStorage('dust-device', 'dust-device');
    await sentDeviceInfo();
}

loadSequence();
heartbeat(5000);
