-- grandMA2 patch export helper
-- Exportuje Fixture a Channel CSV na zvoleny disk
-- 1 = internal drive
-- 4 = USB flash disk (obvykle)
-- Vysledne soubory budou v gma2/importexport na zvolenem disku

return function()
    local function msg(text)
        if gma and gma.feedback then
            gma.feedback(text)
        end
    end

    local function cmd(text)
        msg('CMD: ' .. text)
        gma.cmd(text)
    end

    local function trim(text)
        if text == nil then
            return nil
        end
        return (string.gsub(text, '^%s*(.-)%s*$', '%1'))
    end

    local prefix = 'showbundle'
    local answer = gma.textinput('Patch export file prefix', prefix)
    if answer ~= nil and answer ~= '' then
        prefix = trim(answer)
    end

    local maxFixture = gma.textinput('Max fixture number', '9999')
    if maxFixture == nil or maxFixture == '' then
        maxFixture = '9999'
    end
    maxFixture = trim(maxFixture)

    local maxChannel = gma.textinput('Max channel number', '9999')
    if maxChannel == nil or maxChannel == '' then
        maxChannel = '9999'
    end
    maxChannel = trim(maxChannel)

    local driveNo = gma.textinput('Target drive: 1=internal, 4=USB', '4')
    if driveNo == nil or driveNo == '' then
        driveNo = '4'
    end
    driveNo = trim(driveNo)

    msg('Starting patch export...')
    msg('Selecting target drive ' .. driveNo .. ' ...')
    cmd('SelectDrive ' .. driveNo)

    msg('Exporting Fixture objects...')
    cmd('Export Fixture 1 Thru ' .. maxFixture .. ' "' .. prefix .. '_fixture_patch" /style=csv /transform /o')

    msg('Exporting Channel objects...')
    cmd('Export Channel 1 Thru ' .. maxChannel .. ' "' .. prefix .. '_channel_patch" /style=csv /transform /o')

    msg('Patch export finished.')
    msg('Expected files on selected drive in folder gma2/importexport/:')
    msg('- ' .. prefix .. '_fixture_patch.csv')
    msg('- ' .. prefix .. '_channel_patch.csv')

    if driveNo == '1' then
        msg('Target: internal drive')
    elseif driveNo == '4' then
        msg('Target: USB flash drive')
    else
        msg('Target drive number: ' .. driveNo)
    end
end
