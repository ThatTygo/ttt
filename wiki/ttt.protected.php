<?php
/**
 * Vaste instellingen voor de TTT-wiki. Deze kunnen niet via het beheerscherm
 * worden gewijzigd (protected).
 */
$conf['title'] = 'TTT Wiki';
$conf['tagline'] = 'Trauma Tram Tellers';
$conf['lang'] = 'nl';
$conf['license'] = '0';
$conf['useacl'] = 1;
$conf['authtype'] = 'authttt';
$conf['superuser'] = '@admin';
$conf['manager'] = '@admin';
// Accounts worden beheerd op traumatramtellers.nl.
$conf['disableactions'] = 'register,resendpwd,profile,profile_delete';
// Geen proxy vertrouwen: de wiki ziet zo nooit de IP-adressen van bezoekers.
$conf['trustedproxies'] = [];
$conf['send404'] = 1;
// Toon namen in plaats van loginnamen (ttt12) in de geschiedenis.
$conf['showuseras'] = 'username';
